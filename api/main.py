"""FastAPI endpoints for the conversational agent."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

from agent.agent import ConversationalAgent


class ChatRequest(BaseModel):
    """One chat turn."""

    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = Field(default=None, max_length=64)

    @field_validator("message")
    @classmethod
    def strip_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("message must not be blank")
        return value


class ChatResponse(BaseModel):
    """Chat answer plus the tool trace used by the agent."""

    conversation_id: str
    answer: str
    tools_invoked: list[str]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    agent = ConversationalAgent()
    await agent.initialize()
    app.state.agent = agent
    try:
        yield
    finally:
        await agent.close()


app = FastAPI(
    title="Orion Business Development Agent",
    description="Local LLM agent that discovers FastMCP tools to retrieve read-only prospect data.",
    version="0.2.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    """Liveness endpoint."""
    return {"status": "ok"}


@app.get("/ready", tags=["health"])
async def ready(request: Request) -> dict[str, str]:
    """Readiness endpoint, including whether MCP tools were discovered."""
    agent = getattr(request.app.state, "agent", None)
    if agent is None or not agent.is_ready:
        raise HTTPException(status_code=503, detail="Agent is not ready")
    return {"status": "ready"}


@app.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    """Ask about prospects in natural language."""
    agent: ConversationalAgent = request.app.state.agent
    try:
        result = await agent.chat(payload.message, payload.conversation_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Agent is not ready") from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="The local agent could not complete this request",
        ) from exc
    return ChatResponse(**result)
