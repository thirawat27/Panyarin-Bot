"""Event listeners for Panyari Bot."""

import discord
from discord import app_commands
from discord.ext import commands

from utils import I18n, create_embed
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Events(commands.Cog):
    """Global event handlers."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._original_tree_error = bot.tree.on_error
        bot.tree.on_error = self._on_app_command_error

    def _i18n(self, guild_id: int, key: str, **kwargs) -> str:
        lang = self.bot.guild_settings.get_language(guild_id)
        return I18n.translate(lang, key, **kwargs)

    async def _on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        guild_id = interaction.guild.id if interaction.guild else 0

        if isinstance(error, app_commands.MissingPermissions):
            message = self._i18n(guild_id, "error_no_permission")
        elif isinstance(error, app_commands.BotMissingPermissions):
            message = self._i18n(guild_id, "error_bot_no_permission")
        else:
            message = self._i18n(guild_id, "error_generic", error=str(error))
            logger.exception("Unhandled app command error: %s", error)

        embed = create_embed(
            title="Error",
            description=message,
            color=0xED4245,
        )

        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)

    async def cog_unload(self) -> None:
        self.bot.tree.on_error = self._original_tree_error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Events(bot))
