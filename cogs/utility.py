"""Utility and information commands."""

import discord
from discord import app_commands
from discord.ext import commands

from utils import I18n, create_embed


class Utility(commands.Cog):
    """Server and user information commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def _i18n(self, interaction: discord.Interaction, key: str, **kwargs) -> str:
        guild_id = interaction.guild.id if interaction.guild else 0
        lang = self.bot.guild_settings.get_language(guild_id)
        return I18n.translate(lang, key, **kwargs)

    @app_commands.command(name="serverinfo", description="Show server information")
    async def serverinfo(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            await interaction.response.send_message(
                self._i18n(interaction, "error_not_in_guild"), ephemeral=True
            )
            return

        guild = interaction.guild
        embed = create_embed(
            title=self._i18n(interaction, "serverinfo_title"),
            description=guild.name,
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(
            name="Owner",
            value=guild.owner.mention if guild.owner else "Unknown",
            inline=True,
        )
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(
            name="Created",
            value=f"<t:{int(guild.created_at.timestamp())}:R>",
            inline=True,
        )
        embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Show user information")
    @app_commands.describe(user="User to inspect")
    async def userinfo(
        self,
        interaction: discord.Interaction,
        user: discord.Member | None = None,
    ) -> None:
        target = user or interaction.user
        embed = create_embed(
            title=self._i18n(interaction, "userinfo_title"),
            description=target.mention,
        )
        if target.display_avatar:
            embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="ID", value=target.id, inline=True)
        embed.add_field(
            name="Joined",
            value=f"<t:{int(target.joined_at.timestamp())}:R>",
            inline=True,
        )
        embed.add_field(
            name="Registered",
            value=f"<t:{int(target.created_at.timestamp())}:R>",
            inline=True,
        )
        embed.add_field(
            name="Roles",
            value=", ".join(r.mention for r in target.roles[1:][:10]) or "None",
            inline=False,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Show user avatar")
    @app_commands.describe(user="User to show avatar")
    async def avatar(
        self,
        interaction: discord.Interaction,
        user: discord.Member | None = None,
    ) -> None:
        target = user or interaction.user
        embed = create_embed(
            title=self._i18n(interaction, "avatar_title", user=target.display_name),
        )
        embed.set_image(url=target.display_avatar.url)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utility(bot))
