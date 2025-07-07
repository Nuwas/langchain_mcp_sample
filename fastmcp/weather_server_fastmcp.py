from mcp.server.fastmcp import FastMCP

# Simple weather map
mock_weather = {
    "new york": "Sunny, 25°C",
    "delhi": "Hot, 38°C",
    "london": "Rainy, 17°C",
    "tokyo": "Cloudy, 22°C",
}

# Create MCP server instance
mcp = FastMCP(name="Weather", version="0.1.0")

@mcp.tool(name="weather", description="This tool returns the weather of a city.")
def get_weather(city: str) -> str:
    """Get current weather for a city (mock)."""
    forecast = mock_weather.get(city.lower())
    return forecast if forecast else f"No weather data for {city}."

if __name__ == "__main__":
    mcp.run()