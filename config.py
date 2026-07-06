"""Global configuration for Panyari Bot."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "th")
    COMMAND_GUILD_IDS: list[int] = [
        int(gid.strip())
        for gid in os.getenv("COMMAND_GUILD_IDS", "").split(",")
        if gid.strip().isdigit()
    ]

    LAVALINK_HOST: str = os.getenv("LAVALINK_HOST", "localhost")
    LAVALINK_PORT: int = int(os.getenv("LAVALINK_PORT", "2333"))
    LAVALINK_PASSWORD: str = os.getenv("LAVALINK_PASSWORD", "youshallnotpass")

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DATABASE_PATH: Path = Path(os.getenv("DATABASE_PATH", "data/panyari.db"))

    BOT_NAME: str = "Panyari Bot"

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration values."""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN is required. Please set it in .env file.")
