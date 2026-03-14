"""AI agent logic — manages conversation state and calls OpenAI."""

import logging

from openai import AsyncOpenAI

from app.config import settings
from app.models import AgentResponse, ConversationState, Message, Role

logger = logging.getLogger(__name__)

# In-process conversation store keyed by call SID.
# Production deployments should replace this with a distributed cache (e.g. Redis).
_conversations: dict[str, ConversationState] = {}


def _get_client() -> AsyncOpenAI:
    """Return a configured AsyncOpenAI client."""
    return AsyncOpenAI(api_key=settings.openai_api_key)


def get_or_create_conversation(call_sid: str) -> ConversationState:
    """Return an existing conversation or start a new one."""
    if call_sid not in _conversations:
        _conversations[call_sid] = ConversationState(
            call_sid=call_sid,
            messages=[
                Message(role=Role.SYSTEM, content=settings.system_prompt)
            ],
        )
    return _conversations[call_sid]


def end_conversation(call_sid: str) -> None:
    """Mark a conversation as ended and remove it from the store."""
    _conversations.pop(call_sid, None)


def _build_openai_messages(state: ConversationState) -> list[dict]:
    return [{"role": m.role.value, "content": m.content} for m in state.messages]


_END_PHRASES = {"goodbye", "bye", "hang up", "end call", "that's all", "thats all"}


def _should_end_call(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in _END_PHRASES)


async def process_user_input(call_sid: str, user_text: str) -> AgentResponse:
    """
    Add the user turn to the conversation, call OpenAI, and return the
    assistant's reply together with an end-call signal when appropriate.
    """
    state = get_or_create_conversation(call_sid)

    if not state.is_active:
        return AgentResponse(
            text="This call has already ended. Goodbye!",
            should_end_call=True,
        )

    state.messages.append(Message(role=Role.USER, content=user_text))
    state.turn_count += 1

    # Enforce conversation length limit
    force_end = state.turn_count >= settings.max_conversation_turns

    try:
        client = _get_client()
        completion = await client.chat.completions.create(
            model=settings.openai_model,
            messages=_build_openai_messages(state),
        )
        assistant_text: str = completion.choices[0].message.content or ""
    except Exception:
        logger.exception("OpenAI API call failed for call_sid=%s", call_sid)
        assistant_text = (
            "I'm sorry, I encountered a technical issue. "
            "Please try again in a moment."
        )

    state.messages.append(Message(role=Role.ASSISTANT, content=assistant_text))

    should_end = force_end or _should_end_call(user_text) or _should_end_call(assistant_text)
    if should_end:
        state.is_active = False
        end_conversation(call_sid)

    return AgentResponse(text=assistant_text, should_end_call=should_end)
