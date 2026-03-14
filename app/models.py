"""Pydantic data models for AI Voice Agency."""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    """A single conversation message."""

    role: Role
    content: str


class ConversationState(BaseModel):
    """Tracks the state of an active voice conversation."""

    call_sid: str
    messages: list[Message] = Field(default_factory=list)
    turn_count: int = 0
    is_active: bool = True


class CallWebhookPayload(BaseModel):
    """Incoming webhook payload from Twilio for a new call."""

    CallSid: str
    From: str
    To: str
    CallStatus: str


class SpeechResultPayload(BaseModel):
    """Webhook payload delivered after Twilio gathers speech."""

    CallSid: str
    SpeechResult: str = ""
    Confidence: float = 0.0


class AgentResponse(BaseModel):
    """Response returned by the voice agent."""

    text: str
    should_end_call: bool = False


class HealthResponse(BaseModel):
    """Health-check response body."""

    status: Literal["ok"] = "ok"
    version: str = "1.0.0"
