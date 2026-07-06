"""Tests for internationalization helper."""

from utils.i18n import I18n


def test_load_locales():
    I18n.load_locales()
    assert "th" in I18n.get_supported_languages()
    assert "en" in I18n.get_supported_languages()


def test_translate_thai():
    I18n.load_locales()
    result = I18n.translate("th", "ping_title")
    assert result == "ปิ๊ง!"


def test_translate_english():
    I18n.load_locales()
    result = I18n.translate("en", "ping_title")
    assert result == "Pong!"


def test_translate_with_kwargs():
    I18n.load_locales()
    result = I18n.translate("th", "ping_description", latency=42)
    assert "42" in result


def test_unsupported_key_falls_back():
    I18n.load_locales()
    result = I18n.translate("th", "nonexistent_key")
    assert result == "nonexistent_key"
