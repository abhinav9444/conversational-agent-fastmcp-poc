import pytest
from fastmcp import Client

import mcp_server.tools as tools_module
from mcp_server.server import mcp


class FakeRepository:
    def __init__(self, project):
        self.project = project

    def get_by_name(self, name: str):
        if name.casefold() == "project orion".casefold():
            return self.project
        return None


@pytest.mark.asyncio
async def test_mcp_tool_is_discoverable_and_returns_project(monkeypatch, sample_project) -> None:
    monkeypatch.setattr(tools_module, "_repository", FakeRepository(sample_project))
    async with Client(mcp) as client:
        available = await client.list_tools()
        assert "get_project_information" in {tool.name for tool in available}
        result = await client.call_tool(
            "get_project_information",
            {"project_name": "Project Orion"},
        )
    assert result.data["project_name"] == "Project Orion"
    assert result.data["owner"] == "John Doe"
    assert result.data["budget"] == 500000.0


@pytest.mark.asyncio
async def test_mcp_tool_handles_missing_project(monkeypatch) -> None:
    monkeypatch.setattr(tools_module, "_repository", FakeRepository(None))
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_project_information",
            {"project_name": "Project does not exist"},
        )
    assert result.data["error"] == "Project not found"


@pytest.mark.asyncio
async def test_mcp_tool_rejects_blank_input_gracefully(monkeypatch) -> None:
    monkeypatch.setattr(tools_module, "_repository", FakeRepository(None))
    async with Client(mcp) as client:
        result = await client.call_tool("get_project_information", {"project_name": " "})
    assert result.data["error"] == "Invalid input"
