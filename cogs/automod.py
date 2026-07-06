"""Auto-moderation for spam and mass mentions."""

import time
from collections import defaultdict, deque

import discord
from discord import app_commands
from discord.ext import commands

from utils import I18n, create_embed
from utils.audit import send_audit_log
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AutoMod(commands.Cog):
    """Automatic moderation features."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._message_cache: dict[int, deque[tuple[float, str]]] = defaultdict(
            lambda: deque(maxlen=10)
        )

    def _i18n(self, guild_id: int, key: str, **kwargs) -> str:
        lang = self.bot.guild_settings.get_language(guild_id)
        return I18n.translate(lang, key, **kwargs)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.guild:
            return

        enabled = self.bot.guild_settings.get_setting(
            message.guild.id, "automod_enabled", 0
        )
        if not enabled:
            return

        if await self._check_spam(message) or await self._check_mass_mentions(message):
            try:
                await message.delete()
            except discord.Forbidden:
                logger.warning("Cannot delete spam message in %s", message.channel.id)

    async def _check_spam(self, message: discord.Message) -> bool:
        threshold = self.bot.guild_settings.get_setting(
            message.guild.id, "automod_spam_threshold", 5
        )
        key = (message.guild.id, message.author.id)
        now = time.time()
        cache = self._message_cache[key]
        cache.append((now, message.content))

        recent = [content for timestamp, content in cache if now - timestamp <= 10]
        repeated = sum(1 for content in recent if content == message.content)

        if repeated >= threshold:
            await self._send_warning(message, "automod_spam")
            return True
        return False

    async def _check_mass_mentions(self, message: discord.Message) -> bool:
        max_mentions = self.bot.guild_settings.get_setting(
            message.guild.id, "automod_max_mentions", 5
        )
        if len(message.mentions) >= max_mentions:
            await self._send_warning(message, "automod_mentions")
            return True
        return False

    async def _send_warning(self, message: discord.Message, rule: str) -> None:
        embed = create_embed(
            title=self._i18n(message.guild.id, "automod_spam_title"),
            description=self._i18n(
                message.guild.id,
                "automod_spam_description",
                user=message.author.mention,
            ),
            color=0xED4245,
        )
        try:
            await message.channel.send(embed=embed, delete_after=10)
        except discord.Forbidden:
            pass

        await send_audit_log(
            self.bot,
            message.guild,
            title=f"AutoMod: {rule}",
            description=f"Action taken against {message.author.mention} in {message.channel.mention}",
            color=0xED4245,
        )

    @app_commands.command(name="automod", description="Toggle auto-moderation")
    @app_commands.describe(enabled="Enable or disable auto-moderation")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automod(self, interaction: discord.Interaction, enabled: bool) -> None:
        self.bot.guild_settings.set_setting(
            interaction.guild.id, "automod_enabled", 1 if enabled else 0
        )
        status = "enabled" if enabled else "disabled"
        embed = create_embed(description=f"Auto-moderation is now {status}.")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoMod(bot))
