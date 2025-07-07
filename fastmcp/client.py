from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import StructuredTool
import asyncio
from dotenv import load_dotenv
from typing import Dict, Any
import logging
from concurrent.futures import ThreadPoolExecutor

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Define multiple servers
calculator_server_params = StdioServerParameters(
    command="python",
    args=["fastmcp/calculator_server_fastmcp.py"],
)

weather_server_params = StdioServerParameters(
    command="python",
    args=["fastmcp/weather_server_fastmcp.py"],
)

model = ChatOpenAI(model="gpt-4o")

def should_end(state):
    """Return True when the agent should stop processing."""
    messages = state.get("messages", [])
    if not messages:
        return False
    
    last_message = messages[-1]
    if isinstance(last_message, AIMessage):
        content = last_message.content.lower()
        if (
           ("96" in content or "final answer" in content) or
            ("delhi" in content or "weather" in content)
        ):
            return True
    return False

def run_mcp_tool_sync(server_params, tool_name, kwargs):
    """Call the MCP tool in a separate thread with its own event loop."""
    def run_in_thread():
        async def call_mcp_server():
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Call the tool directly via MCP
                    #logger.info(f"Going to invoke tool {tool_name} with: {kwargs}")
                    result = await session.call_tool(
                        name=tool_name,
                        arguments=kwargs
                    )
                    return result.content[0].text if result.content else "No result"
        
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(call_mcp_server())
        finally:
            loop.close()
    
    with ThreadPoolExecutor() as executor:
        future = executor.submit(run_in_thread)
        return future.result(timeout=30)

async def load_tools_from_server(server_params):
    """Load tools from a specific MCP server."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            return tools, server_params

async def run_agent():
    try:
        logger.info("Starting MCP client connections...")
        
        # Load tools from both servers
        all_tools = []
        server_tool_mapping = {}
        
        # Load calculator tools
        logger.info("Loading calculator tools...")
        calc_tools, calc_server = await load_tools_from_server(calculator_server_params)
        logger.info(f"Loaded {len(calc_tools)} calculator tools: {[t.name for t in calc_tools]}")
        all_tools.extend(calc_tools)
        for tool in calc_tools:
            server_tool_mapping[tool.name] = calc_server
        
        # Load weather tools
        logger.info("Loading weather tools...")
        try:
            weather_tools, weather_server = await load_tools_from_server(weather_server_params)
            logger.info(f"Loaded {len(weather_tools)} weather tools: {[t.name for t in weather_tools]}")
            all_tools.extend(weather_tools)
            for tool in weather_tools:
                server_tool_mapping[tool.name] = weather_server
        except Exception as e:
            logger.error(f"Failed to load weather tools: {e}")
        
        logger.info(f"Total tools loaded: {len(all_tools)}")
        
        # Create sync tools that call the appropriate MCP server
        sync_tools = []
        for mcp_tool in all_tools:
            def create_sync_wrapper(tool_name, server_params):
                def sync_func(**kwargs):
                    try:
                        logger.info(f"Sync wrapper called for {tool_name} with: {kwargs}")
                        return run_mcp_tool_sync(server_params, tool_name, kwargs)
                    except Exception as e:
                        logger.error(f"Tool execution error: {e}")
                        return f"Error executing tool: {e}"
                return sync_func
            
            sync_tool = StructuredTool(
                name=mcp_tool.name,
                description=mcp_tool.description,
                func=create_sync_wrapper(mcp_tool.name, server_tool_mapping[mcp_tool.name]),
                args_schema=mcp_tool.args_schema
            )
            sync_tools.append(sync_tool)
        
        logger.info(f"Created {len(sync_tools)} sync tools: {[tool.name for tool in sync_tools]}")


        # Create a custom system prompt that explains available tools
        system_message = f"""You are an AI assistant with access to the following MCP tools:
        
Available tools:
{chr(10).join([f"- {tool.name}: {tool.description}" for tool in sync_tools])}

If a user asks for something that cannot be handled by these tools, respond with:
"I don't have an MCP server configured to handle this request. I can only help with:
- Mathematical calculations (using the multiply tool)
- Weather information (using the weather tool)

Please ask me something related to these capabilities."

Only use the available tools for appropriate tasks. Do not suggest unrelated tasks."""

        # Create the agent node with sync tools and system prompt
        agent_node = create_react_agent(model, sync_tools)

        # Create the StateGraph
        graph = StateGraph(state_schema=Dict[str, Any])
        graph.add_node("agent", agent_node)
        
        graph.add_conditional_edges(
            "agent",
            should_end,
            {
                True: END,
                False: "agent"
            }
        )
        
        graph.set_entry_point("agent")
        runnable = graph.compile()

        # Initial state
        initial_state = {
            "messages": [
                SystemMessage(content=system_message),
                HumanMessage(content="what's (3 + 5) x 12?")
            ]
        }
        logger.info("Starting agent execution...")
        output = runnable.invoke(initial_state)
        print("Answer:", output["messages"][-1].content)

        # Initial state - Ask for both calculation and weather
        initial_state = {
            "messages": [
                SystemMessage(content=system_message),
                HumanMessage(content="what's the weather in Delhi?")
            ]
            #"messages": [HumanMessage(content="what's (3 + 5) x 12? And after that, what's the weather in Delhi?")]
        }
        logger.info("Starting agent execution...")
        output = runnable.invoke(initial_state)
        print("Answer:", output["messages"][-1].content)


        initial_state = {
            "messages": [
                SystemMessage(content=system_message),
                HumanMessage(content="Who is the owner of kl46e0803")
            ]
            #"messages": [HumanMessage(content="what's (3 + 5) x 12? And after that, what's the weather in Delhi?")]
        }
        logger.info("Starting agent execution...")
        output = runnable.invoke(initial_state)
        
        print("Answer:", output["messages"][-1].content)

    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(run_agent())