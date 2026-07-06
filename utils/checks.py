"""Permission and precondition checks."""

from typing import Callable

import discord
from discord import app_commands


def has_required_permissions(**perms: bool) -> Callable:
    """Decorator to check if the bot has required permissions."""

    def predicate(interaction: discord.Interaction) -> bool:
        if not interaction.guild:
            return False
        permissions = interaction.guild.me.guild_permissions
        missing = [
            name for name, value in perms.items() if getattr(permissions, name) != value
        ]
        if missing:
            raise app_commands.MissingPermissions(missing)
        return True

    return app_commands.check(predicate)
