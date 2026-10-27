"""Small process-local conversation memory for the POC."""

import asyncio
from collections import defaultdict
from typing import Any


class ConversationMemory:
    """Keep only user/assistant turns; tool payloads are not stored as long-term memory."""

    def __init__(self, max_messages: int = 20) -> None:
        self._max_messages = max_messages
        self._histories: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def get_history(self, conversation_id: str) -> list[dict[str, Any]]:
        """Return a copy so callers cannot mutate shared state."""
        async with self._lock:
            return [message.copy() for message in self._histories[conversation_id]]

    async def append_turn(self, conversation_id: str, user_message: str, answer: str) -> None:
        """Store one exchange and trim history to the configured bound."""
        async with self._lock:
            history = self._histories[conversation_id]
            history.extend(
                [
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": answer},
                ]
            )
            self._histories[conversation_id] = history[-self._max_messages :]

    async def clear(self, conversation_id: str) -> None:
        """Delete a conversation from process-local memory."""
        async with self._lock:
            self._histories.pop(conversation_id, None)
