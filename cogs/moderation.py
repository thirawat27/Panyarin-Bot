"""Administration and moderation commands."""

import datetime

import discord
from discord import app_commands
from discord.ext import commands

from utils import I18n, create_embed
from utils.audit import send_audit_log


class Moderation(commands.Cog):
    """Server management and moderation commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def _i18n(self, interaction: discord.Interaction, key: str, **kwargs) -> str:
        guild_id = interaction.guild.id if interaction.guild else 0
        lang = self.bot.guild_settings.get_language(guild_id)
        return I18n.translate(lang, key, **kwargs)

    @app_commands.command(name="kick", description="เตะสมาชิก / Kick a member")
    @app_commands.describe(user="สมาชิกที่ต้องการเตะ", reason="เหตุผล")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str | None = None,
    ) -> None:
        reason = reason or "No reason provided"
        await user.kick(reason=reason)

        embed = create_embed(
            title=self._i18n(interaction, "kick_title"),
            description=self._i18n(interaction, "kick_success", user=user.mention),
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)

        await send_audit_log(
            self.bot,
            interaction.guild,
            title=self._i18n(interaction, "kick_title"),
            description=self._i18n(interaction, "kick_success", user=str(user)),
            fields=[
                ("Reason", reason, False),
                ("Moderator", interaction.user.mention, True),
            ],
            color=0xFAA61A,
        )

    @app_commands.command(name="ban", description="แบนสมาชิก / Ban a member")
    @app_commands.describe(
        user="สมาชิกที่ต้องการแบน",
        reason="เหตุผล",
        delete_days="ลบข้อความย้อนหลังกี่วัน (0-7)",
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str | None = None,
        delete_days: app_commands.Range[int, 0, 7] = 0,
    ) -> None:
        reason = reason or "No reason provided"
        await user.ban(reason=reason, delete_message_days=delete_days)

        embed = create_embed(
            title=self._i18n(interaction, "ban_title"),
            description=self._i18n(interaction, "ban_success", user=user.mention),
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)

        await send_audit_log(
            self.bot,
            interaction.guild,
            title=self._i18n(interaction, "ban_title"),
            description=self._i18n(interaction, "ban_success", user=str(user)),
            fields=[
                ("Reason", reason, False),
                ("Moderator", interaction.user.mention, True),
            ],
            color=0xED4245,
        )

    @app_commands.command(name="unban", description="ปลดแบนผู้ใช้ / Unban a user")
    @app_commands.describe(user_id="ID ของผู้ใช้ที่ต้องการปลดแบน")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str) -> None:
        if not user_id.isdigit():
            await interaction.response.send_message("Invalid user ID", ephemeral=True)
            return

        user = discord.Object(id=int(user_id))
        await interaction.guild.unban(user)

        embed = create_embed(
            title=self._i18n(interaction, "unban_title"),
            description=self._i18n(interaction, "unban_success", user=f"<@{user_id}>"),
        )
        await interaction.response.send_message(embed=embed)

        await send_audit_log(
            self.bot,
            interaction.guild,
            title=self._i18n(interaction, "unban_title"),
            description=self._i18n(interaction, "unban_success", user=f"<@{user_id}>"),
            fields=[("Moderator", interaction.user.mention, True)],
            color=0x57F287,
        )

    @app_commands.command(
        name="timeout", description="ระงับสมาชิกชั่วคราว / Timeout a member"
    )
    @app_commands.describe(user="สมาชิก", minutes="จำนวนนาที", reason="เหตุผล")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        minutes: app_commands.Range[int, 1, 40320],
        reason: str | None = None,
    ) -> None:
        reason = reason or "No reason provided"
        until = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
        await user.timeout(until, reason=reason)

        embed = create_embed(
            title=self._i18n(interaction, "timeout_title"),
            description=self._i18n(
                interaction, "timeout_success", user=user.mention, duration=minutes
            ),
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)

        await send_audit_log(
            self.bot,
            interaction.guild,
            title=self._i18n(interaction, "timeout_title"),
            description=self._i18n(
                interaction, "timeout_success", user=str(user), duration=minutes
            ),
            fields=[
                ("Reason", reason, False),
                ("Moderator", interaction.user.mention, True),
            ],
            color=0xFAA61A,
        )

    @app_commands.command(name="warn", description="เตือนสมาชิก / Warn a member")
    @app_commands.describe(user="สมาชิก", reason="เหตุผล")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str,
    ) -> None:
        self.bot.guild_settings.add_warning(
            interaction.guild.id, user.id, interaction.user.id, reason
        )
        count = self.bot.guild_settings.count_warnings(interaction.guild.id, user.id)

        embed = create_embed(
            title=self._i18n(interaction, "warn_title"),
            description=self._i18n(interaction, "warn_success", user=user.mention),
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(
            name=self._i18n(
                interaction, "warn_count", user=user.display_name, count=count
            ),
            value="",
            inline=False,
        )
        await interaction.response.send_message(embed=embed)

        await send_audit_log(
            self.bot,
            interaction.guild,
            title=self._i18n(interaction, "warn_title"),
            description=self._i18n(interaction, "warn_success", user=str(user)),
            fields=[
                ("Reason", reason, False),
                ("Moderator", interaction.user.mention, True),
                ("Total warnings", str(count), True),
            ],
            color=0xFAA61A,
        )

    @app_commands.command(
        name="warnings", description="ดูประวัติการเตือน / View warnings"
    )
    @app_commands.describe(user="สมาชิก")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warnings(
        self, interaction: discord.Interaction, user: discord.Member
    ) -> None:
        rows = self.bot.guild_settings.get_warnings(interaction.guild.id, user.id)
        count = len(rows)

        embed = create_embed(
            title=self._i18n(interaction, "warn_title"),
            description=self._i18n(
                interaction, "warn_count", user=user.mention, count=count
            ),
        )
        for row in rows[:10]:
            warn_id, moderator_id, reason, created_at = row
            moderator = interaction.guild.get_member(moderator_id)
            embed.add_field(
                name=f"Warning #{warn_id}",
                value=f"Reason: {reason}\nBy: {moderator.mention if moderator else moderator_id}\nAt: {created_at}",
                inline=False,
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="purge", description="ลบข้อความในช่อง / Purge messages")
    @app_commands.describe(amount="จำนวนข้อความที่ต้องการลบ (1-100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[int, 1, 100],
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)

        embed = create_embed(
            title=self._i18n(interaction, "purge_title"),
            description=self._i18n(interaction, "purge_success", count=len(deleted)),
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

        await send_audit_log(
            self.bot,
            interaction.guild,
            title=self._i18n(interaction, "purge_title"),
            description=self._i18n(interaction, "purge_success", count=len(deleted)),
            fields=[
                ("Channel", interaction.channel.mention, True),
                ("Moderator", interaction.user.mention, True),
            ],
            color=0xED4245,
        )

    @app_commands.command(name="slowmode", description="ตั้งค่าโหมดช้า / Set slowmode")
    @app_commands.describe(seconds="จำนวนวินาที (0-21600)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode(
        self,
        interaction: discord.Interaction,
        seconds: app_commands.Range[int, 0, 21600],
    ) -> None:
        await interaction.channel.edit(slowmode_delay=seconds)

        embed = create_embed(
            title=self._i18n(interaction, "slowmode_title"),
            description=self._i18n(interaction, "slowmode_success", seconds=seconds),
        )
        await interaction.response.send_message(embed=embed)

        await send_audit_log(
            self.bot,
            interaction.guild,
            title=self._i18n(interaction, "slowmode_title"),
            description=self._i18n(interaction, "slowmode_success", seconds=seconds),
            fields=[
                ("Channel", interaction.channel.mention, True),
                ("Moderator", interaction.user.mention, True),
            ],
            color=0x5865F2,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderation(bot))
