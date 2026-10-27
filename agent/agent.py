"""Tool-calling conversational agent built on a local OpenAI-compatible endpoint."""

import json
import logging
from typing import Any
from uuid import uuid4

from openai import AsyncOpenAI

from agent.memory import ConversationMemory
from agent.mcp_client import MCPToolClient
from agent.prompts import SYSTEM_PROMPT
from config import Settings, get_settings

logger = logging.getLogger(__name__)


class ConversationalAgent:
    """LLM orchestration layer; all project-data access goes through MCP."""

    def __init__(
        self,
        settings: Settings | None = None,
        mcp_client: MCPToolClient | None = None,
        llm_client: AsyncOpenAI | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.mcp_client = mcp_client or MCPToolClient(settings=self.settings)
        self.llm_client = llm_client or AsyncOpenAI(
            base_url=self.settings.llm_base_url,
            api_key=self.settings.llm_api_key,
        )
        self.memory = ConversationMemory(self.settings.max_history_messages)
        self._initialized = False

    @property
    def is_ready(self) -> bool:
        return self._initialized and bool(self.mcp_client.tool_names)

    async def initialize(self) -> None:
        """Discover MCP tools before accepting chat requests."""
        await self.mcp_client.discover_tools()
        self._initialized = True

    async def close(self) -> None:
        """Close the local LLM client's HTTP connection pool."""
        await self.llm_client.close()

    async def chat(self, user_message: str, conversation_id: str | None = None) -> dict[str, Any]:
        """Answer a turn, invoke discovered tools as needed, and retain conversational context."""
        if not self.is_ready:
            raise RuntimeError("Agent is not initialized; MCP tool discovery has not completed")

        conversation_id = conversation_id or str(uuid4())
        user_message = user_message.strip()
        history = await self.memory.get_history(conversation_id)
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *history,
            {"role": "user", "content": user_message},
        ]
        tools_invoked: list[str] = []

        for _ in range(self.settings.max_tool_rounds):
            response = await self.llm_client.chat.completions.create(
                model=self.settings.llm_model,
                messages=messages,
                tools=self.mcp_client.openai_tools,
                tool_choice="auto",
                temperature=0.1,
            )
            assistant_message = response.choices[0].message
            if not assistant_message.tool_calls:
                answer = assistant_message.content or "I couldn't produce an answer for that request."
                await self.memory.append_turn(conversation_id, user_message, answer)
                return {
                    "conversation_id": conversation_id,
                    "answer": answer,
                    "tools_invoked": tools_invoked,
                }

            messages.append(assistant_message.model_dump(exclude_none=True))
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tools_invoked.append(tool_name)
                try:
                    arguments = json.loads(tool_call.function.arguments or "{}")
                    if not isinstance(arguments, dict):
                        raise ValueError("Tool arguments must be a JSON object")
                    result = await self.mcp_client.call_tool(tool_name, arguments)
                except Exception:
                    logger.exception("agent_tool_call_failed tool=%s", tool_name)
                    result = {"error": "Tool invocation failed"}
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, ensure_ascii=False, default=str),
                    }
                )

        response = await self.llm_client.chat.completions.create(
            model=self.settings.llm_model,
            messages=messages,
            tools=self.mcp_client.openai_tools,
            tool_choice="none",
            temperature=0.1,
        )
        answer = response.choices[0].message.content or (
            "I reached the tool-call limit before I could complete the answer."
        )
        await self.memory.append_turn(conversation_id, user_message, answer)
        return {
            "conversation_id": conversation_id,
            "answer": answer,
            "tools_invoked": tools_invoked,
        }
