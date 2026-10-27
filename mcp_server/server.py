"""FastMCP server entry point."""

import logging

from fastmcp import FastMCP

from mcp_server.tools import get_project_information

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

mcp = FastMCP("Project Orion Data Server")
mcp.tool(get_project_information)


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
