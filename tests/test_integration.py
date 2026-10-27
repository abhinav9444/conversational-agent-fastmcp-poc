"""Opt-in integration test against a running FastMCP HTTP service."""

import os

import pytest
from fastmcp import Client


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION_TESTS") != "1",
    reason="set RUN_INTEGRATION_TESTS=1 to call the running MCP server",
)


@pytest.mark.asyncio
async def test_running_mcp_server_returns_seeded_prospects() -> None:
    url = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
    async with Client(url) as client:
        tools = await client.list_tools()
        assert "get_prospects" in {tool.name for tool in tools}
        result = await client.call_tool("get_prospects", {"region": "Europe"})
    assert result.data["total_count"] >= 1
    assert all(row["region"] == "Europe" for row in result.data["prospects"])
