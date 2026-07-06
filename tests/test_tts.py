"""Tests for TTS helper functions."""

from cogs.tts import _language_from_voice


def test_language_from_voice():
    assert _language_from_voice("th-TH-PremwadeeNeural") == "th-TH"
    assert _language_from_voice("en-US-AriaNeural") == "en-US"
    assert _language_from_voice("ja-JP-NanamiNeural") == "ja-JP"


def test_language_from_short_name():
    assert _language_from_voice("Unknown") == "Unknown"
