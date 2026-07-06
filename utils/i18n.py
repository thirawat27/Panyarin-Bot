"""Internationalization helper for Panyari Bot."""

import json
from pathlib import Path
from typing import Any

from config import Config


class I18n:
    """Loads locale files and provides formatted translations."""

    _locales: dict[str, dict[str, str]] = {}

    @classmethod
    def load_locales(cls) -> None:
        locale_dir = Path(__file__).parent.parent / "locales"
        for file in locale_dir.glob("*.json"):
            lang = file.stem
            with open(file, "r", encoding="utf-8") as f:
                cls._locales[lang] = json.load(f)

    @classmethod
    def get_supported_languages(cls) -> list[str]:
        return list(cls._locales.keys())

    @classmethod
    def get_language_name(cls, lang: str) -> str:
        return cls._locales.get(lang, {}).get("language_name", lang)

    @classmethod
    def translate(cls, lang: str, key: str, **kwargs: Any) -> str:
        if not cls._locales:
            cls.load_locales()

        message = cls._locales.get(
            lang, cls._locales.get(Config.DEFAULT_LANGUAGE, {})
        ).get(key, key)
        try:
            return message.format(**kwargs)
        except KeyError:
            return message

    @classmethod
    def is_supported(cls, lang: str) -> bool:
        return lang in cls._locales
