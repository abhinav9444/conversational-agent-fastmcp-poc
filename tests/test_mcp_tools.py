import pytest
from fastmcp import Client

import mcp_server.tools as tools_module
from mcp_server.server import mcp


class FakeRepository:
    def __init__(self, prospects):
        self.prospects = prospects

    def get_prospects(self, industry=None, stage=None, region=None, risk_level=None, limit=100):
        rows = self.prospects
        if industry:
            rows = [row for row in rows if row.industry.casefold() == industry.casefold()]
        if stage:
            rows = [row for row in rows if row.opportunity_stage == stage]
        if region:
            rows = [row for row in rows if row.region == region]
        if risk_level:
            rows = [row for row in rows if row.risk_level == risk_level]
        return rows


@pytest.mark.asyncio
async def test_prospects_tool_is_discoverable_and_returns_filtered_records(monkeypatch, sample_prospect) -> None:
    monkeypatch.setattr(tools_module, "_repository", FakeRepository([sample_prospect]))
    async with Client(mcp) as client:
        available = await client.list_tools()
        assert "get_prospects" in {tool.name for tool in available}
        result = await client.call_tool(
            "get_prospects",
            {"industry": "Biotech", "region": "Europe", "risk_level": "High"},
        )
    assert result.data["total_count"] == 1
    assert result.data["prospects"][0]["company_name"] == "HelixNova Biologics"
    assert result.data["prospects"][0]["opportunity_value_usd"] == 2400000.0


@pytest.mark.asyncio
async def test_prospects_tool_returns_empty_array_for_no_match(monkeypatch) -> None:
    monkeypatch.setattr(tools_module, "_repository", FakeRepository([]))
    async with Client(mcp) as client:
        result = await client.call_tool("get_prospects", {"industry": "Biotech"})
    assert result.data["prospects"] == []
    assert result.data["total_count"] == 0


@pytest.mark.asyncio
async def test_prospects_tool_rejects_unsupported_region(monkeypatch) -> None:
    monkeypatch.setattr(tools_module, "_repository", FakeRepository([]))
    async with Client(mcp) as client:
        result = await client.call_tool("get_prospects", {"region": "Mars"})
    assert result.data["error"] == "Invalid input"
