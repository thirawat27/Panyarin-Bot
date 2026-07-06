"""Audit log helper for moderation actions."""

import discord

from utils import create_embed


async def send_audit_log(
    bot: discord.Client,
    guild: discord.Guild,
    title: str,
    description: str,
    fields: list[tuple[str, str, bool]] | None = None,
    color: int = 0x5865F2,
) -> None:
    """Send an audit log embed to the configured audit channel."""
    from db import GuildSettings

    settings = GuildSettings()
    channel_id = settings.get_setting(guild.id, "audit_log_channel_id")
    if not channel_id:
        return

    channel = guild.get_channel(int(channel_id))
    if not isinstance(channel, discord.TextChannel):
        return

    embed = create_embed(title=title, description=description, color=color)
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

    try:
        await channel.send(embed=embed)
    except discord.Forbidden:
        pass
