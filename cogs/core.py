"""Core cog with ping, help, and language settings."""

import discord
from discord import app_commands
from discord.ext import commands

from utils import I18n, create_embed


class Core(commands.Cog):
    """Core system commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def _i18n(self, interaction: discord.Interaction, key: str, **kwargs) -> str:
        guild_id = interaction.guild.id if interaction.guild else 0
        lang = self.bot.guild_settings.get_language(guild_id)
        return I18n.translate(lang, key, **kwargs)

    @app_commands.command(
        name="ping", description="ตรวจสอบความหน่วงของบอท / Check bot latency"
    )
    async def ping(self, interaction: discord.Interaction) -> None:
        latency = round(self.bot.latency * 1000)
        embed = create_embed(
            title=self._i18n(interaction, "ping_title"),
            description=self._i18n(interaction, "ping_description", latency=latency),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="help", description="แสดงคำสั่งทั้งหมด / Show all commands"
    )
    async def help_command(self, interaction: discord.Interaction) -> None:
        lang = self.bot.guild_settings.get_language(
            interaction.guild.id if interaction.guild else 0
        )
        embed = create_embed(
            title=self._i18n(interaction, "help_title"),
            description=self._i18n(interaction, "help_description"),
        )

        categories = {
            "help_category_core": "/ping, /help, /setlanguage",
            "help_category_admin": "/kick, /ban, /unban, /timeout, /purge, /slowmode",
            "help_category_moderation": "/warn",
            "help_category_music": "/play, /pause, /resume, /skip, /queue, /volume, /loop, /leave",
            "help_category_fun": "/dice, /coinflip, /8ball, /poll, /ask",
            "help_category_utility": "/serverinfo, /userinfo, /avatar",
            "help_category_tts": "/tts, /tts_voices, /tts_languages, /tts_setlanguage, /tts_setvoice",
        }

        for key, commands_list in categories.items():
            embed.add_field(
                name=I18n.translate(lang, key),
                value=commands_list,
                inline=False,
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="setlanguage",
        description="ตั้งค่าภาษาของบอท / Set bot language",
    )
    @app_commands.choices(
        language=[
            app_commands.Choice(name="ไทย", value="th"),
            app_commands.Choice(name="English", value="en"),
        ]
    )
    async def setlanguage(
        self,
        interaction: discord.Interaction,
        language: app_commands.Choice[str],
    ) -> None:
        if not interaction.guild:
            await interaction.response.send_message(
                self._i18n(interaction, "error_not_in_guild"), ephemeral=True
            )
            return

        if not I18n.is_supported(language.value):
            supported = ", ".join(I18n.get_supported_languages())
            await interaction.response.send_message(
                self._i18n(interaction, "setlanguage_invalid", languages=supported),
                ephemeral=True,
            )
            return

        self.bot.guild_settings.set_language(interaction.guild.id, language.value)
        embed = create_embed(
            title=self._i18n(interaction, "setlanguage_title"),
            description=self._i18n(
                interaction,
                "setlanguage_success",
                language=I18n.get_language_name(language.value),
            ),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Core(bot))
