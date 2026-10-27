"""Opt-in integration test against a running FastMCP HTTP service."""

import os

import pytest
from fastmcp import Client


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION_TESTS") != "1",
    reason="set RUN_INTEGRATION_TESTS=1 to call the running MCP server",
)


@pytest.mark.asyncio
async def test_running_mcp_server_returns_seeded_orion() -> None:
    url = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
    async with Client(url) as client:
        tools = await client.list_tools()
        assert "get_project_information" in {tool.name for tool in tools}
        result = await client.call_tool(
            "get_project_information",
            {"project_name": "Project Orion"},
        )
    assert result.data["project_name"] == "Project Orion"
    assert result.data["owner"] == "John Doe"
    assert result.data["budget"] == 500000.0
