"""MCP tool discovery and invocation gateway."""

import asyncio
import json
import logging
from typing import Any

from fastmcp import Client

from config import Settings, get_settings

logger = logging.getLogger(__name__)


class MCPToolClient:
    """Discover tool schemas dynamically and invoke only discovered tools."""

    def __init__(self, server_url: str | None = None, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._server_url = server_url or self._settings.mcp_server_url
        self._tool_schemas: dict[str, dict[str, Any]] = {}
        self._openai_tools: list[dict[str, Any]] = []

    @property
    def openai_tools(self) -> list[dict[str, Any]]:
        """Expose discovered tools in the format expected by OpenAI-compatible APIs."""
        return [tool.copy() for tool in self._openai_tools]

    @property
    def tool_names(self) -> set[str]:
        return set(self._tool_schemas)

    async def discover_tools(self) -> list[dict[str, Any]]:
        """List MCP tools, retrying while the MCP service starts."""
        last_error: Exception | None = None
        for attempt in range(1, self._settings.mcp_discovery_attempts + 1):
            try:
                async with Client(self._server_url) as client:
                    discovered = await client.list_tools()
                schemas: dict[str, dict[str, Any]] = {}
                openai_tools: list[dict[str, Any]] = []
                for tool in discovered:
                    dumped = tool.model_dump(by_alias=True) if hasattr(tool, "model_dump") else {}
                    input_schema = (
                        getattr(tool, "inputSchema", None)
                        or getattr(tool, "input_schema", None)
                        or dumped.get("inputSchema")
                        or dumped.get("input_schema")
                        or {"type": "object", "properties": {}}
                    )
                    if not isinstance(input_schema, dict):
                        input_schema = {"type": "object", "properties": {}}
                    schema = {
                        "name": tool.name,
                        "description": getattr(tool, "description", None) or "",
                        "input_schema": input_schema,
                    }
                    schemas[tool.name] = schema
                    openai_tools.append(
                        {
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": schema["description"],
                                "parameters": input_schema,
                            },
                        }
                    )
                if not openai_tools:
                    raise RuntimeError("MCP server connected but exposed no tools")
                self._tool_schemas = schemas
                self._openai_tools = openai_tools
                logger.info("mcp_tools_discovered count=%d names=%s", len(schemas), sorted(schemas))
                return self.openai_tools
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "mcp_tool_discovery_attempt_failed attempt=%d/%d error=%s",
                    attempt,
                    self._settings.mcp_discovery_attempts,
                    type(exc).__name__,
                )
                if attempt < self._settings.mcp_discovery_attempts:
                    await asyncio.sleep(self._settings.mcp_discovery_retry_seconds)
        raise RuntimeError("Could not discover tools from the configured MCP server") from last_error

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Invoke a tool only if it was returned by tools/list during discovery."""
        if name not in self._tool_schemas:
            raise ValueError(f"Tool {name!r} was not discovered from the MCP server")
        async with Client(self._server_url) as client:
            result = await client.call_tool(name, arguments)
        data = getattr(result, "data", None)
        if data is not None:
            return data
        content = getattr(result, "content", []) or []
        text_blocks = [item.text for item in content if hasattr(item, "text")]
        if len(text_blocks) == 1:
            try:
                return json.loads(text_blocks[0])
            except json.JSONDecodeError:
                return text_blocks[0]
        return text_blocks
