"""Tests for app/agent.py — AI agent logic (OpenAI mocked)."""

import pytest

from app.agent import (
    _should_end_call,
    end_conversation,
    get_or_create_conversation,
    process_user_input,
)
from app.models import Role


# ---------------------------------------------------------------------------
# Pure unit tests (no I/O)
# ---------------------------------------------------------------------------


def test_get_or_create_conversation_new():
    state = get_or_create_conversation("CA_NEW_001")
    assert state.call_sid == "CA_NEW_001"
    # System prompt should be the first message
    assert state.messages[0].role == Role.SYSTEM
    end_conversation("CA_NEW_001")  # clean up


def test_get_or_create_conversation_returns_same():
    state1 = get_or_create_conversation("CA_SAME_001")
    state2 = get_or_create_conversation("CA_SAME_001")
    assert state1 is state2
    end_conversation("CA_SAME_001")


def test_end_conversation_removes_state():
    get_or_create_conversation("CA_END_001")
    end_conversation("CA_END_001")
    # Creating again should produce a fresh state (turn_count == 0)
    fresh = get_or_create_conversation("CA_END_001")
    assert fresh.turn_count == 0
    end_conversation("CA_END_001")


@pytest.mark.parametrize(
    "text, expected",
    [
        ("goodbye", True),
        ("bye", True),
        ("hang up", True),
        ("end call please", True),
        ("that's all for now", True),
        ("What is the weather?", False),
        ("Tell me more", False),
    ],
)
def test_should_end_call(text, expected):
    assert _should_end_call(text) is expected


# ---------------------------------------------------------------------------
# Integration tests (OpenAI mocked via monkeypatch)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_process_user_input_normal_turn(monkeypatch):
    """Agent returns assistant reply; call is not ended."""

    async def mock_create(**kwargs):
        class Choice:
            message = type("Msg", (), {"content": "The weather is sunny."})()

        class Completion:
            choices = [Choice()]

        return Completion()

    class MockChat:
        completions = type("C", (), {"create": staticmethod(mock_create)})()

    class MockClient:
        chat = MockChat()

    monkeypatch.setattr("app.agent._get_client", lambda: MockClient())

    response = await process_user_input("CA_MOCK_001", "What is the weather?")
    assert response.text == "The weather is sunny."
    assert response.should_end_call is False
    end_conversation("CA_MOCK_001")


@pytest.mark.asyncio
async def test_process_user_input_goodbye_ends_call(monkeypatch):
    """Saying 'goodbye' triggers end-of-call flag."""

    async def mock_create(**kwargs):
        class Choice:
            message = type("Msg", (), {"content": "Take care, goodbye!"})()

        class Completion:
            choices = [Choice()]

        return Completion()

    class MockChat:
        completions = type("C", (), {"create": staticmethod(mock_create)})()

    class MockClient:
        chat = MockChat()

    monkeypatch.setattr("app.agent._get_client", lambda: MockClient())

    response = await process_user_input("CA_BYE_001", "goodbye")
    assert response.should_end_call is True


@pytest.mark.asyncio
async def test_process_user_input_api_error_returns_fallback(monkeypatch):
    """When OpenAI raises an exception the agent returns a graceful fallback."""

    async def mock_create(**kwargs):
        raise RuntimeError("API down")

    class MockChat:
        completions = type("C", (), {"create": staticmethod(mock_create)})()

    class MockClient:
        chat = MockChat()

    monkeypatch.setattr("app.agent._get_client", lambda: MockClient())

    response = await process_user_input("CA_ERR_001", "Hello")
    assert "technical issue" in response.text.lower()
    end_conversation("CA_ERR_001")
