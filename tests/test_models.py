"""Tests for app/models.py."""

import pytest

from app.models import (
    AgentResponse,
    CallWebhookPayload,
    ConversationState,
    HealthResponse,
    Message,
    Role,
    SpeechResultPayload,
)


def test_message_creation():
    msg = Message(role=Role.USER, content="Hello!")
    assert msg.role == Role.USER
    assert msg.content == "Hello!"


def test_conversation_state_defaults():
    state = ConversationState(call_sid="CA123")
    assert state.call_sid == "CA123"
    assert state.messages == []
    assert state.turn_count == 0
    assert state.is_active is True


def test_agent_response_default_no_end():
    resp = AgentResponse(text="Hi there")
    assert resp.text == "Hi there"
    assert resp.should_end_call is False


def test_agent_response_with_end():
    resp = AgentResponse(text="Goodbye!", should_end_call=True)
    assert resp.should_end_call is True


def test_call_webhook_payload():
    payload = CallWebhookPayload(
        CallSid="CA001",
        From="+1234567890",
        To="+0987654321",
        CallStatus="ringing",
    )
    assert payload.CallSid == "CA001"
    assert payload.CallStatus == "ringing"


def test_speech_result_payload_defaults():
    payload = SpeechResultPayload(CallSid="CA002")
    assert payload.SpeechResult == ""
    assert payload.Confidence == 0.0


def test_health_response_defaults():
    resp = HealthResponse()
    assert resp.status == "ok"
    assert resp.version == "1.0.0"


def test_role_values():
    assert Role.SYSTEM.value == "system"
    assert Role.USER.value == "user"
    assert Role.ASSISTANT.value == "assistant"
