import json
from types import SimpleNamespace

import pytest

from agent.agent import ConversationalAgent
from config import Settings


class FakeMCPClient:
    def __init__(self):
        self.tool_names = set()
        self.calls = []
        self._tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_project_information",
                    "description": "Retrieve a project record.",
                    "parameters": {
                        "type": "object",
                        "properties": {"project_name": {"type": "string"}},
                        "required": ["project_name"],
                    },
                },
            }
        ]

    @property
    def openai_tools(self):
        return self._tools

    async def discover_tools(self):
        self.tool_names = {"get_project_information"}
        return self._tools

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        return {
            "project_name": arguments["project_name"],
            "owner": "John Doe",
            "status": "Active",
            "budget": 500000.0,
        }


class FakeMessage:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []

    def model_dump(self, exclude_none=True):
        return {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
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
                    name="get_project_information",
                    arguments=json.dumps({"project_name": "Project Orion"}),
                ),
            )
            message = FakeMessage(tool_calls=[tool_call])
        else:
            message = FakeMessage(
                content="Project Orion is active, owned by John Doe, with a budget of $500,000."
            )
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeLLMClient:
    def __init__(self):
        self.completions = FakeCompletions()
        self.chat = SimpleNamespace(completions=self.completions)
        self.closed = False

    async def close(self):
        self.closed = True


@pytest.mark.asyncio
async def test_agent_discovers_and_invokes_tool_then_summarizes() -> None:
    settings = Settings(mcp_discovery_attempts=1, max_tool_rounds=2)
    mcp_client = FakeMCPClient()
    llm_client = FakeLLMClient()
    agent = ConversationalAgent(settings=settings, mcp_client=mcp_client, llm_client=llm_client)

    await agent.initialize()
    result = await agent.chat("Tell me about Project Orion")

    assert result["tools_invoked"] == ["get_project_information"]
    assert "John Doe" in result["answer"]
    assert mcp_client.calls == [
        ("get_project_information", {"project_name": "Project Orion"})
    ]
    assert (await agent.memory.get_history(result["conversation_id"]))[-1]["content"] == result["answer"]
    await agent.close()
    assert llm_client.closed
