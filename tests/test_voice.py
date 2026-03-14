"""Tests for app/voice.py — TwiML builders."""

from app.voice import build_gather_twiml, build_say_and_hangup_twiml, speech_action_url


def test_build_gather_twiml_structure():
    twiml = build_gather_twiml("Hello, how can I help?", "https://example.com/speech")
    assert '<?xml version="1.0" encoding="UTF-8"?>' in twiml
    assert "<Response>" in twiml
    assert "<Gather" in twiml
    assert "input=\"speech\"" in twiml
    assert "action=\"https://example.com/speech\"" in twiml
    assert "Hello, how can I help?" in twiml
    assert "<Hangup" in twiml


def test_build_gather_twiml_has_fallback():
    twiml = build_gather_twiml("How are you?", "https://example.com/speech")
    # There should be a <Say> fallback outside the Gather
    assert twiml.count("<Say>") >= 2


def test_build_say_and_hangup_twiml_structure():
    twiml = build_say_and_hangup_twiml("Goodbye!")
    assert '<?xml version="1.0" encoding="UTF-8"?>' in twiml
    assert "<Response>" in twiml
    assert "Goodbye!" in twiml
    assert "<Hangup" in twiml
    assert "<Gather" not in twiml


def test_speech_action_url_contains_call_sid(monkeypatch):
    monkeypatch.setattr("app.voice.settings.app_base_url", "https://myapp.example.com")
    url = speech_action_url("CA_TEST_123")
    assert url == "https://myapp.example.com/voice/speech/CA_TEST_123"
