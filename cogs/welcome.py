"""Welcome and goodbye messages."""

import discord
from discord import app_commands
from discord.ext import commands

from utils import I18n, create_embed
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Welcome(commands.Cog):
    """Member join/leave announcements."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def _i18n(self, guild_id: int, key: str, **kwargs) -> str:
        lang = self.bot.guild_settings.get_language(guild_id)
        return I18n.translate(lang, key, **kwargs)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        channel_id = self.bot.guild_settings.get_setting(
            member.guild.id, "welcome_channel_id"
        )
        if not channel_id:
            return

        channel = member.guild.get_channel(int(channel_id))
        if not isinstance(channel, discord.TextChannel):
            return

        embed = create_embed(
            title=self._i18n(member.guild.id, "welcome_title"),
            description=self._i18n(
                member.guild.id,
                "welcome_description",
                member=member.mention,
                guild=member.guild.name,
            ),
            color=0x57F287,
        )
        if member.display_avatar:
            embed.set_thumbnail(url=member.display_avatar.url)

        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            logger.warning(
                "Missing permission to send welcome message in %s", channel.id
            )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        channel_id = self.bot.guild_settings.get_setting(
            member.guild.id, "goodbye_channel_id"
        )
        if not channel_id:
            return

        channel = member.guild.get_channel(int(channel_id))
        if not isinstance(channel, discord.TextChannel):
            return

        embed = create_embed(
            title=self._i18n(member.guild.id, "goodbye_title"),
            description=self._i18n(
                member.guild.id,
                "goodbye_description",
                member=member.mention,
                guild=member.guild.name,
            ),
            color=0xED4245,
        )

        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            logger.warning(
                "Missing permission to send goodbye message in %s", channel.id
            )

    @app_commands.command(name="setwelcome", description="Set welcome channel")
    @app_commands.describe(channel="Channel for welcome messages")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setwelcome(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
    ) -> None:
        self.bot.guild_settings.set_setting(
            interaction.guild.id, "welcome_channel_id", channel.id
        )
        embed = create_embed(description=f"Welcome channel set to {channel.mention}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setgoodbye", description="Set goodbye channel")
    @app_commands.describe(channel="Channel for goodbye messages")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setgoodbye(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
    ) -> None:
        self.bot.guild_settings.set_setting(
            interaction.guild.id, "goodbye_channel_id", channel.id
        )
        embed = create_embed(description=f"Goodbye channel set to {channel.mention}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setaudit", description="Set audit log channel")
    @app_commands.describe(channel="Channel for audit logs")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setaudit(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
    ) -> None:
        self.bot.guild_settings.set_setting(
            interaction.guild.id, "audit_log_channel_id", channel.id
        )
        embed = create_embed(description=f"Audit log channel set to {channel.mention}")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Welcome(bot))
