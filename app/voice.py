"""Voice utilities — build TwiML responses for Twilio calls."""

from xml.etree.ElementTree import Element, SubElement, tostring

from app.config import settings

_GATHER_TIMEOUT = 5  # seconds of silence before Twilio stops gathering
_GATHER_SPEECH_TIMEOUT = "auto"  # let Twilio decide when the caller stops


def build_gather_twiml(prompt: str, action_url: str) -> str:
    """
    Build a TwiML Response that:
      1. Says the given prompt aloud (text-to-speech).
      2. Gathers the caller's spoken reply.
      3. Posts the SpeechResult to *action_url*.

    Returns the TwiML as an XML string.
    """
    response = Element("Response")
    gather = SubElement(
        response,
        "Gather",
        attrib={
            "input": "speech",
            "action": action_url,
            "method": "POST",
            "timeout": str(_GATHER_TIMEOUT),
            "speechTimeout": _GATHER_SPEECH_TIMEOUT,
        },
    )
    say = SubElement(gather, "Say")
    say.text = prompt

    # Fallback if the caller doesn't say anything
    fallback_say = SubElement(response, "Say")
    fallback_say.text = "I didn't catch that. Goodbye!"
    SubElement(response, "Hangup")

    return '<?xml version="1.0" encoding="UTF-8"?>' + tostring(response, encoding="unicode")


def build_say_and_hangup_twiml(message: str) -> str:
    """
    Build a TwiML Response that says the message and hangs up.
    Used as the final turn in a conversation.
    """
    response = Element("Response")
    say = SubElement(response, "Say")
    say.text = message
    SubElement(response, "Hangup")

    return '<?xml version="1.0" encoding="UTF-8"?>' + tostring(response, encoding="unicode")


def speech_action_url(call_sid: str) -> str:
    """Return the absolute URL Twilio should POST the speech result to."""
    return f"{settings.app_base_url}/voice/speech/{call_sid}"
