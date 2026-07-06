"""Music cog using Lavalink via wavelink."""

import discord
import wavelink
from discord import app_commands
from discord.ext import commands

from utils import I18n, create_embed


class Music(commands.Cog):
    """Music playback commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def _i18n(self, interaction: discord.Interaction, key: str, **kwargs) -> str:
        guild_id = interaction.guild.id if interaction.guild else 0
        lang = self.bot.guild_settings.get_language(guild_id)
        return I18n.translate(lang, key, **kwargs)

    async def _ensure_voice(
        self, interaction: discord.Interaction
    ) -> wavelink.Player | None:
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message(
                self._i18n(interaction, "music_not_in_voice"),
                ephemeral=True,
            )
            return None

        if not interaction.guild.voice_client:
            player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
        else:
            player = interaction.guild.voice_client

        return player

    @app_commands.command(
        name="play", description="เล่นเพลงจาก YouTube / Play music from YouTube"
    )
    @app_commands.describe(query="ชื่อเพลงหรือลิงก์")
    async def play(self, interaction: discord.Interaction, query: str) -> None:
        player = await self._ensure_voice(interaction)
        if not player:
            return

        await interaction.response.defer()

        tracks = await wavelink.Playable.search(query)
        if not tracks:
            await interaction.followup.send("ไม่พบเพลง / No tracks found")
            return

        track = tracks[0]
        player.autoplay = wavelink.AutoPlayMode.disabled

        if player.playing:
            player.queue.put(track)
            embed = create_embed(
                title=self._i18n(interaction, "music_queue_title"),
                description=self._i18n(
                    interaction, "music_added_to_queue", title=track.title
                ),
            )
        else:
            await player.play(track, volume=50)
            embed = create_embed(
                title=self._i18n(interaction, "music_now_playing"),
                description=self._i18n(
                    interaction, "music_now_playing", title=track.title
                ),
            )
            embed.add_field(name="Artist", value=track.author, inline=True)
            embed.add_field(
                name="Duration", value=self._format_duration(track.length), inline=True
            )

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="pause", description="หยุดเพลงชั่วคราว / Pause music")
    async def pause(self, interaction: discord.Interaction) -> None:
        player = interaction.guild.voice_client
        if not player or not isinstance(player, wavelink.Player):
            await interaction.response.send_message(
                self._i18n(interaction, "music_no_player"), ephemeral=True
            )
            return

        await player.pause(True)
        embed = create_embed(description=self._i18n(interaction, "music_paused"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="resume", description="เล่นเพลงต่อ / Resume music")
    async def resume(self, interaction: discord.Interaction) -> None:
        player = interaction.guild.voice_client
        if not player or not isinstance(player, wavelink.Player):
            await interaction.response.send_message(
                self._i18n(interaction, "music_no_player"), ephemeral=True
            )
            return

        await player.pause(False)
        embed = create_embed(description=self._i18n(interaction, "music_resumed"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="skip", description="ข้ามเพลง / Skip song")
    async def skip(self, interaction: discord.Interaction) -> None:
        player = interaction.guild.voice_client
        if not player or not isinstance(player, wavelink.Player):
            await interaction.response.send_message(
                self._i18n(interaction, "music_no_player"), ephemeral=True
            )
            return

        await player.skip()
        embed = create_embed(description=self._i18n(interaction, "music_skipped"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="queue", description="แสดงคิวเพลง / Show queue")
    async def queue(self, interaction: discord.Interaction) -> None:
        player = interaction.guild.voice_client
        if not player or not isinstance(player, wavelink.Player):
            await interaction.response.send_message(
                self._i18n(interaction, "music_no_player"), ephemeral=True
            )
            return

        if player.queue.is_empty:
            embed = create_embed(
                description=self._i18n(interaction, "music_queue_empty")
            )
        else:
            embed = create_embed(title=self._i18n(interaction, "music_queue_title"))
            for index, track in enumerate(player.queue[:20], start=1):
                embed.add_field(
                    name=f"{index}. {track.title}",
                    value=track.author or "Unknown",
                    inline=False,
                )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="nowplaying", description="เพลงที่กำลังเล่น / Now playing"
    )
    async def nowplaying(self, interaction: discord.Interaction) -> None:
        player = interaction.guild.voice_client
        if not player or not isinstance(player, wavelink.Player) or not player.current:
            await interaction.response.send_message(
                self._i18n(interaction, "music_no_player"), ephemeral=True
            )
            return

        track = player.current
        embed = create_embed(
            title=self._i18n(interaction, "music_now_playing"),
            description=f"[{track.title}]({track.uri})",
        )
        embed.add_field(name="Artist", value=track.author, inline=True)
        embed.add_field(
            name="Duration", value=self._format_duration(track.length), inline=True
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="volume", description="ตั้งค่าระดับเสียง / Set volume")
    @app_commands.describe(level="ระดับเสียง 0-100")
    async def volume(
        self,
        interaction: discord.Interaction,
        level: app_commands.Range[int, 0, 100],
    ) -> None:
        player = interaction.guild.voice_client
        if not player or not isinstance(player, wavelink.Player):
            await interaction.response.send_message(
                self._i18n(interaction, "music_no_player"), ephemeral=True
            )
            return

        await player.set_volume(level)
        embed = create_embed(
            description=self._i18n(interaction, "music_volume_set", volume=level)
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="loop", description="เปิด/ปิด วนเพลง / Toggle loop")
    async def loop(self, interaction: discord.Interaction) -> None:
        player = interaction.guild.voice_client
        if not player or not isinstance(player, wavelink.Player):
            await interaction.response.send_message(
                self._i18n(interaction, "music_no_player"), ephemeral=True
            )
            return

        player.queue.mode = (
            wavelink.QueueMode.loop
            if player.queue.mode != wavelink.QueueMode.loop
            else wavelink.QueueMode.normal
        )

        message = (
            self._i18n(interaction, "music_loop_enabled")
            if player.queue.mode == wavelink.QueueMode.loop
            else self._i18n(interaction, "music_loop_disabled")
        )
        embed = create_embed(description=message)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="leave", description="ออกจากช่องเสียง / Leave voice channel"
    )
    async def leave(self, interaction: discord.Interaction) -> None:
        player = interaction.guild.voice_client
        if not player or not isinstance(player, wavelink.Player):
            await interaction.response.send_message(
                self._i18n(interaction, "music_bot_not_in_voice"), ephemeral=True
            )
            return

        await player.disconnect()
        embed = create_embed(description=self._i18n(interaction, "music_left_channel"))
        await interaction.response.send_message(embed=embed)

    @staticmethod
    def _format_duration(milliseconds: int) -> str:
        seconds = milliseconds // 1000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Music(bot))
