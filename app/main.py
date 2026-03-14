"""FastAPI application — entry point for all HTTP endpoints."""

import logging

from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import JSONResponse

from app.agent import end_conversation, get_or_create_conversation, process_user_input
from app.config import settings
from app.models import HealthResponse
from app.voice import build_gather_twiml, build_say_and_hangup_twiml, speech_action_url

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Voice Agency",
    description=(
        "An AI-powered voice agency that handles inbound phone calls using "
        "OpenAI language models and Twilio telephony."
    ),
    version="1.0.0",
)

_TWIML_CONTENT_TYPE = "application/xml"

_GREETING = (
    "Hello! You've reached the AI Voice Agency. "
    "How can I help you today?"
)


@app.get("/health", response_model=HealthResponse, tags=["meta"])
async def health_check() -> HealthResponse:
    """Return application health status."""
    return HealthResponse()


@app.post("/voice/inbound", tags=["voice"])
async def inbound_call(
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    CallStatus: str = Form(...),
) -> Response:
    """
    Twilio webhook — called when a new inbound call arrives.
    Greets the caller and starts gathering their first message.
    """
    logger.info("Inbound call CallSid=%s From=%s To=%s Status=%s", CallSid, From, To, CallStatus)
    get_or_create_conversation(CallSid)

    twiml = build_gather_twiml(
        prompt=_GREETING,
        action_url=speech_action_url(CallSid),
    )
    return Response(content=twiml, media_type=_TWIML_CONTENT_TYPE)


@app.post("/voice/speech/{call_sid}", tags=["voice"])
async def handle_speech(
    call_sid: str,
    SpeechResult: str = Form(default=""),
    Confidence: float = Form(default=0.0),
) -> Response:
    """
    Twilio webhook — called after the caller speaks.
    Passes the transcription to the AI agent and returns the next TwiML prompt.
    """
    logger.info(
        "Speech received call_sid=%s text=%r confidence=%.2f",
        call_sid,
        SpeechResult,
        Confidence,
    )

    if not SpeechResult.strip():
        twiml = build_say_and_hangup_twiml(
            "I didn't catch that. Thank you for calling. Goodbye!"
        )
        end_conversation(call_sid)
        return Response(content=twiml, media_type=_TWIML_CONTENT_TYPE)

    agent_response = await process_user_input(call_sid, SpeechResult)

    if agent_response.should_end_call:
        twiml = build_say_and_hangup_twiml(agent_response.text)
    else:
        twiml = build_gather_twiml(
            prompt=agent_response.text,
            action_url=speech_action_url(call_sid),
        )

    return Response(content=twiml, media_type=_TWIML_CONTENT_TYPE)


@app.post("/voice/status", tags=["voice"])
async def call_status(
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
) -> JSONResponse:
    """
    Twilio webhook — called on call status changes (completed, failed, etc.).
    Cleans up in-memory conversation state.
    """
    logger.info("Call status update CallSid=%s Status=%s", CallSid, CallStatus)
    if CallStatus in {"completed", "failed", "busy", "no-answer", "canceled"}:
        end_conversation(CallSid)
    return JSONResponse({"received": True})
