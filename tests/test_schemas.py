import pytest
from pydantic import ValidationError

from api.main import ChatRequest
from mcp_server.schemas import ProjectLookupInput


def test_project_lookup_strips_name() -> None:
    payload = ProjectLookupInput(project_name="  Project Orion  ")
    assert payload.project_name == "Project Orion"


def test_project_lookup_rejects_blank_name() -> None:
    with pytest.raises(ValidationError):
        ProjectLookupInput(project_name="   ")


def test_chat_request_trims_message() -> None:
    payload = ChatRequest(message="  Tell me about Project Orion  ")
    assert payload.message == "Tell me about Project Orion"


def test_chat_request_rejects_blank_message() -> None:
    with pytest.raises(ValidationError):
        ChatRequest(message=" ")
