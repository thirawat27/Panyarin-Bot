"""Entry point for Panyari Bot."""

import asyncio
from pathlib import Path

import discord
import wavelink
from discord.ext import commands

from config import Config
from db import GuildSettings
from utils.i18n import I18n
from utils.logger import setup_logger

logger = setup_logger()


class PanyariBot(commands.Bot):
    """Main bot class for Panyari."""

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.voice_states = True

        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            help_command=None,
        )
        self.guild_settings = GuildSettings()

    async def setup_hook(self) -> None:
        I18n.load_locales()
        await self._load_cogs()
        await self._setup_lavalink()

    async def _load_cogs(self) -> None:
        cogs_dir = Path(__file__).parent / "cogs"
        for cog_file in sorted(cogs_dir.glob("*.py")):
            if cog_file.name.startswith("_"):
                continue
            cog_name = f"cogs.{cog_file.stem}"
            try:
                await self.load_extension(cog_name)
                logger.info("Loaded cog: %s", cog_name)
            except Exception as exc:
                logger.error("Failed to load cog %s: %s", cog_name, exc)

    async def _setup_lavalink(self) -> None:
        nodes = [
            wavelink.Node(
                uri=f"http://{Config.LAVALINK_HOST}:{Config.LAVALINK_PORT}",
                password=Config.LAVALINK_PASSWORD,
            )
        ]
        await wavelink.Pool.connect(nodes=nodes, client=self, cache_capacity=100)

    async def on_ready(self) -> None:
        logger.info("%s is ready | Logged in as %s", Config.BOT_NAME, self.user)
        try:
            synced = await self.tree.sync()
            logger.info("Synced %d slash commands", len(synced))
        except Exception as exc:
            logger.error("Failed to sync commands: %s", exc)

    async def on_wavelink_node_ready(
        self, payload: wavelink.NodeReadyEventPayload
    ) -> None:
        logger.info("Lavalink node ready: %s", payload.node)


async def main() -> None:
    Config.validate()
    bot = PanyariBot()
    async with bot:
        await bot.start(Config.DISCORD_TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
