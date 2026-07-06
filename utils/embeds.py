"""Embed builders for Panyari Bot."""

import discord

from config import Config


def create_embed(
    title: str | None = None,
    description: str | None = None,
    color: int = 0x5865F2,
    footer: str | None = None,
) -> discord.Embed:
    """Create a styled Discord embed."""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
    )
    if footer:
        embed.set_footer(text=footer)
    else:
        embed.set_footer(text=Config.BOT_NAME)
    return embed
