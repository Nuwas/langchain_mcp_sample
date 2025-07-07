from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="Calculator", version="0.1.0")

@mcp.tool(name="multiply", description="Multiply two numbers in the format 'a*b'")
def multiply(expression: str) -> str:
    a, b = map(int, expression.split("*"))
    return str(a * b)

if __name__ == "__main__":
    mcp.run()
