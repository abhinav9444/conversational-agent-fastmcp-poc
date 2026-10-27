import pytest

from agent.memory import ConversationMemory


@pytest.mark.asyncio
async def test_memory_keeps_bounded_user_assistant_turns() -> None:
    memory = ConversationMemory(max_messages=4)
    await memory.append_turn("conversation", "first question", "first answer")
    await memory.append_turn("conversation", "second question", "second answer")
    await memory.append_turn("conversation", "third question", "third answer")

    history = await memory.get_history("conversation")
    assert len(history) == 4
    assert history[0]["content"] == "second question"
    assert history[-1]["content"] == "third answer"
    await memory.clear("conversation")
    assert await memory.get_history("conversation") == []
