"""SQLite wrapper for guild-specific settings."""

import sqlite3
from pathlib import Path
from typing import Optional

from config import Config


class GuildSettings:
    """Manages per-guild configuration persisted in SQLite."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = db_path or Config.DATABASE_PATH
        self._ensure_db()

    def _connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self.db_path)

    def _ensure_db(self) -> None:
        schema_path = Path(__file__).parent / "schema.sql"
        with self._connect() as conn, open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

    def get_language(self, guild_id: int) -> str:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT language FROM guild_settings WHERE guild_id = ?", (guild_id,)
            ).fetchone()
            return row[0] if row else Config.DEFAULT_LANGUAGE

    def set_language(self, guild_id: int, language: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO guild_settings (guild_id, language)
                VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET language = excluded.language
                """,
                (guild_id, language),
            )

    def get_setting(self, guild_id: int, key: str, default=None):
        with self._connect() as conn:
            row = conn.execute(
                f"SELECT {key} FROM guild_settings WHERE guild_id = ?", (guild_id,)
            ).fetchone()
            return row[0] if row else default

    def set_setting(self, guild_id: int, key: str, value) -> None:
        with self._connect() as conn:
            conn.execute(
                f"""
                INSERT INTO guild_settings (guild_id, {key})
                VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET {key} = excluded.{key}
                """,
                (guild_id, value),
            )

    def get_tts_language(self, guild_id: int) -> str | None:
        return self.get_setting(guild_id, "tts_language")

    def set_tts_language(self, guild_id: int, language: str) -> None:
        self.set_setting(guild_id, "tts_language", language)

    def get_tts_voice(self, guild_id: int) -> str | None:
        return self.get_setting(guild_id, "tts_voice")

    def set_tts_voice(self, guild_id: int, voice: str) -> None:
        self.set_setting(guild_id, "tts_voice", voice)

    def add_warning(
        self, guild_id: int, user_id: int, moderator_id: int, reason: str
    ) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO warnings (guild_id, user_id, moderator_id, reason)
                VALUES (?, ?, ?, ?)
                """,
                (guild_id, user_id, moderator_id, reason),
            )
            return cursor.lastrowid

    def count_warnings(self, guild_id: int, user_id: int) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM warnings WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id),
            ).fetchone()
            return row[0]

    def get_warnings(self, guild_id: int, user_id: int):
        with self._connect() as conn:
            return conn.execute(
                """
                SELECT id, moderator_id, reason, created_at
                FROM warnings
                WHERE guild_id = ? AND user_id = ?
                ORDER BY created_at DESC
                """,
                (guild_id, user_id),
            ).fetchall()
