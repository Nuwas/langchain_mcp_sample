


# Terminal -1

* python3 -m venv venv
* source venv/bin/activate
* pip install -r requiremnts.txt
* pip install langchain_mcp_adapters
* pip install fastmcp
* python3 fastmcp/calculator_server_fastmcp.py


# Terminal -2

source venv/bin/activate
python3 fastmcp/weather_server_fastmcp.py


# Terminal -3

source venv/bin/activate
python3 fastmcp/client.py

# Result 


(venv) nuwasponnambathayil@WC954XW39W sample_gen_ai % python3 fastmcp/client.py
INFO:__main__:Starting MCP client connections...
INFO:__main__:Loading calculator tools...
[07/07/25 12:32:49] INFO     Processing request of type                server.py:523
                             ListToolsRequest                                       
INFO:__main__:Loaded 1 calculator tools: ['multiply']
INFO:__main__:Loading weather tools...
[07/07/25 12:32:49] INFO     Processing request of type                server.py:523
                             ListToolsRequest                                       
INFO:__main__:Loaded 1 weather tools: ['weather']
INFO:__main__:Total tools loaded: 2
INFO:__main__:Created 2 sync tools: ['multiply', 'weather']
INFO:__main__:Starting agent execution...
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:__main__:Sync wrapper called for multiply with: {'expression': '8*12'}
[07/07/25 12:32:50] INFO     Processing request of type                server.py:523
                             CallToolRequest                                        
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Answer: The result of \((3 + 5) \times 12\) is 96.
INFO:__main__:Starting agent execution...
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:__main__:Sync wrapper called for weather with: {'city': 'Delhi'}
[07/07/25 12:32:53] INFO     Processing request of type                server.py:523
                             CallToolRequest                                        
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Answer: The weather in Delhi is currently hot, with a temperature of 38°C.
INFO:__main__:Starting agent execution...
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Answer: I don't have an MCP server configured to handle this request. I can only help with:
- Mathematical calculations (using the multiply tool)
- Weather information (using the weather tool)

Please ask me something related to these capabilities.
(venv) nuwasponnambathayil@WC954XW39W sample_gen_ai % 
