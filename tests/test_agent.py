import json
from types import SimpleNamespace

import pytest

from agent.agent import ConversationalAgent
from config import Settings


class FakeMCPClient:
    def __init__(self):
        self.tool_names = set()
        self.calls = []
        self._tools = [{
            "type": "function",
            "function": {
                "name": "get_prospects",
                "description": "Retrieve prospect records.",
                "parameters": {"type": "object", "properties": {"region": {"type": "string"}}},
            },
        }]

    @property
    def openai_tools(self):
        return self._tools

    async def discover_tools(self):
        self.tool_names = {"get_prospects"}
        return self._tools

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        return {"prospects": [{"company_name": "HelixNova Biologics", "opportunity_value_usd": 2400000}], "total_count": 1}


class FakeMessage:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []

    def model_dump(self, exclude_none=True):
        return {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {"id": call.id, "type": "function", "function": {
                    "name": call.function.name, "arguments": call.function.arguments
                }}
                for call in self.tool_calls
            ],
        }


class FakeCompletions:
    def __init__(self):
        self.count = 0
        self.seen_messages = []

    async def create(self, **kwargs):
        self.count += 1
        self.seen_messages.append(kwargs["messages"])
        if self.count == 1:
            tool_call = SimpleNamespace(
                id="call-1",
                function=SimpleNamespace(
                    name="get_prospects",
                    arguments=json.dumps({"region": "Europe"}),
                ),
            )
            message = FakeMessage(tool_calls=[tool_call])
        else:
            message = FakeMessage(content="One fictional prospect is listed at $2,400,000.")
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeLLMClient:
    def __init__(self):
        self.completions = FakeCompletions()
        self.chat = SimpleNamespace(completions=self.completions)
        self.closed = False

    async def close(self):
        self.closed = True


@pytest.mark.asyncio
async def test_agent_discovers_and_invokes_prospect_tool_then_summarizes() -> None:
    settings = Settings(mcp_discovery_attempts=1, max_tool_rounds=2)
    mcp_client = FakeMCPClient()
    llm_client = FakeLLMClient()
    agent = ConversationalAgent(settings=settings, mcp_client=mcp_client, llm_client=llm_client)

    await agent.initialize()
    result = await agent.chat("Show prospects in Europe")

    assert result["tools_invoked"] == ["get_prospects"]
    assert "$2,400,000" in result["answer"]
    assert mcp_client.calls == [("get_prospects", {"region": "Europe"})]
    assert (await agent.memory.get_history(result["conversation_id"]))[-1]["content"] == result["answer"]
    await agent.close()
    assert llm_client.closed
