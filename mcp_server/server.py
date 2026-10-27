"""FastMCP server entry point."""

import logging

from fastmcp import FastMCP

from mcp_server.tools import get_prospects

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

mcp = FastMCP("Lonza Business Development Data Server")
mcp.tool(get_prospects)


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)
