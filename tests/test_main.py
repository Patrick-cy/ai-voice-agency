"""Tests for the FastAPI application endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data


# ---------------------------------------------------------------------------
# Inbound call
# ---------------------------------------------------------------------------


def test_inbound_call_returns_twiml():
    resp = client.post(
        "/voice/inbound",
        data={
            "CallSid": "CA_INBOUND_001",
            "From": "+1234567890",
            "To": "+0987654321",
            "CallStatus": "ringing",
        },
    )
    assert resp.status_code == 200
    assert "application/xml" in resp.headers["content-type"]
    body = resp.text
    assert "<Gather" in body
    assert "AI Voice Agency" in body


# ---------------------------------------------------------------------------
# Speech handler
# ---------------------------------------------------------------------------


def test_speech_handler_empty_input_hangs_up():
    resp = client.post(
        "/voice/speech/CA_SPEECH_EMPTY",
        data={"SpeechResult": "", "Confidence": "0.0"},
    )
    assert resp.status_code == 200
    assert "<Hangup" in resp.text
    assert "<Gather" not in resp.text


@pytest.mark.asyncio
async def test_speech_handler_normal_response(monkeypatch):
    """With mocked OpenAI the handler returns a Gather TwiML."""

    async def mock_create(**kwargs):
        class Choice:
            message = type("Msg", (), {"content": "Sure, I can help with that."})()

        class Completion:
            choices = [Choice()]

        return Completion()

    class MockChat:
        completions = type("C", (), {"create": staticmethod(mock_create)})()

    class MockClient:
        chat = MockChat()

    monkeypatch.setattr("app.agent._get_client", lambda: MockClient())

    resp = client.post(
        "/voice/speech/CA_SPEECH_001",
        data={"SpeechResult": "Can you help me?", "Confidence": "0.9"},
    )
    assert resp.status_code == 200
    assert "<Gather" in resp.text
    assert "Sure, I can help with that." in resp.text


# ---------------------------------------------------------------------------
# Status webhook
# ---------------------------------------------------------------------------


def test_call_status_completed():
    # Seed a conversation first
    from app.agent import get_or_create_conversation

    get_or_create_conversation("CA_STATUS_001")
    resp = client.post(
        "/voice/status",
        data={"CallSid": "CA_STATUS_001", "CallStatus": "completed"},
    )
    assert resp.status_code == 200
    assert resp.json()["received"] is True


def test_call_status_unknown_does_not_crash():
    resp = client.post(
        "/voice/status",
        data={"CallSid": "CA_STATUS_UNK", "CallStatus": "in-progress"},
    )
    assert resp.status_code == 200
