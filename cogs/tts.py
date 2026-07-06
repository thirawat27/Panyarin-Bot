"""Text-to-speech cog using Microsoft Edge TTS."""

import asyncio
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import ClassVar

import discord
import edge_tts
from discord import app_commands
from discord.ext import commands

from utils import I18n, create_embed


def _language_from_voice(voice_name: str) -> str:
    """Extract locale prefix from edge-tts voice name."""
    parts = voice_name.split("-")
    if len(parts) >= 2:
        return f"{parts[0]}-{parts[1]}"
    return voice_name


class TTS(commands.Cog):
    """Text-to-speech commands with multi-language and multi-voice support."""

    _voices_cache: ClassVar[list[dict] | None] = None

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._temp_dir = Path(tempfile.gettempdir()) / "panyari_tts"
        self._temp_dir.mkdir(parents=True, exist_ok=True)

    def _i18n(self, interaction: discord.Interaction, key: str, **kwargs) -> str:
        guild_id = interaction.guild.id if interaction.guild else 0
        lang = self.bot.guild_settings.get_language(guild_id)
        return I18n.translate(lang, key, **kwargs)

    @classmethod
    async def _list_voices(cls) -> list[dict]:
        if cls._voices_cache is None:
            cls._voices_cache = await edge_tts.list_voices()
        return cls._voices_cache

    async def _voices_for_language(self, language: str) -> list[dict]:
        voices = await self._list_voices()
        return [
            v for v in voices if v["ShortName"].lower().startswith(language.lower())
        ]

    def _default_tts_language(self, guild_id: int) -> str:
        configured = self.bot.guild_settings.get_tts_language(guild_id)
        if configured:
            return configured
        guild_lang = self.bot.guild_settings.get_language(guild_id)
        return "th-TH" if guild_lang == "th" else "en-US"

    @app_commands.command(
        name="tts", description="พูดข้อความด้วยเสียง / Speak text in voice channel"
    )
    @app_commands.describe(
        message="ข้อความที่ต้องการให้พูด",
        language="ภาษา (เว้นว่างใช้ค่าตั้งต้นของเซิร์ฟเวอร์)",
        voice_model="โมเดลเสียง (เว้นว่างใช้ค่าตั้งต้นของเซิร์ฟเวอร์)",
    )
    async def tts(
        self,
        interaction: discord.Interaction,
        message: str,
        language: str | None = None,
        voice_model: str | None = None,
    ) -> None:
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message(
                self._i18n(interaction, "tts_not_in_voice"),
                ephemeral=True,
            )
            return

        if interaction.guild.voice_client is not None:
            await interaction.response.send_message(
                self._i18n(interaction, "tts_music_playing"),
                ephemeral=True,
            )
            return

        if not shutil.which("ffmpeg"):
            await interaction.response.send_message(
                self._i18n(interaction, "tts_ffmpeg_missing"),
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        guild_id = interaction.guild.id if interaction.guild else 0
        voices = await self._list_voices()

        language = language or self._default_tts_language(guild_id)

        available_voices = [
            v for v in voices if v["ShortName"].lower().startswith(language.lower())
        ]
        if not available_voices:
            supported = sorted({v["Locale"] for v in voices})
            await interaction.followup.send(
                self._i18n(
                    interaction,
                    "tts_language_invalid",
                    languages=", ".join(supported[:20]),
                ),
                ephemeral=True,
            )
            return

        configured_voice = self.bot.guild_settings.get_tts_voice(guild_id)
        voice = voice_model or configured_voice
        if voice is None or not any(v["ShortName"] == voice for v in available_voices):
            voice = available_voices[0]["ShortName"]

        output_path = self._temp_dir / f"tts_{uuid.uuid4().hex}.mp3"
        try:
            communicate = edge_tts.Communicate(message, voice)
            await communicate.save(str(output_path))
        except Exception as exc:
            await interaction.followup.send(
                self._i18n(interaction, "tts_generation_failed", error=str(exc)),
                ephemeral=True,
            )
            return

        channel = interaction.user.voice.channel
        try:
            voice_client = await channel.connect()
        except Exception as exc:
            await interaction.followup.send(
                self._i18n(interaction, "tts_connection_failed", error=str(exc)),
                ephemeral=True,
            )
            return

        embed = create_embed(
            description=self._i18n(
                interaction,
                "tts_speaking",
                language=language,
                voice=voice,
            ),
        )
        await interaction.followup.send(embed=embed)

        def after_play(error):
            if error:
                print(f"TTS playback error: {error}")
            asyncio.run_coroutine_threadsafe(voice_client.disconnect(), self.bot.loop)
            try:
                output_path.unlink(missing_ok=True)
            except OSError:
                pass

        voice_client.play(discord.FFmpegPCMAudio(str(output_path)), after=after_play)

    @app_commands.command(
        name="tts_voices",
        description="แสดงรายการโมเดลเสียง / List available TTS voices",
    )
    @app_commands.describe(language="ภาษา เช่น th-TH, en-US")
    async def tts_voices(
        self,
        interaction: discord.Interaction,
        language: str | None = None,
    ) -> None:
        voices = await self._list_voices()

        if language:
            voices = [
                v for v in voices if v["ShortName"].lower().startswith(language.lower())
            ]
        else:
            guild_lang = self.bot.guild_settings.get_language(
                interaction.guild.id if interaction.guild else 0
            )
            default_locale = "th-TH" if guild_lang == "th" else "en-US"
            voices = [
                v
                for v in voices
                if v["ShortName"].lower().startswith(default_locale.lower())
            ]

        if not voices:
            await interaction.response.send_message(
                self._i18n(interaction, "tts_no_voices"),
                ephemeral=True,
            )
            return

        embed = create_embed(
            title=self._i18n(interaction, "tts_voices_title"),
            description=self._i18n(interaction, "tts_voices_description"),
        )
        for voice in voices[:25]:
            name = voice["ShortName"]
            gender = voice.get("Gender", "Unknown")
            embed.add_field(name=name, value=gender, inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="tts_languages",
        description="แสดงรายการภาษาที่รองรับ / List supported TTS languages",
    )
    async def tts_languages(self, interaction: discord.Interaction) -> None:
        voices = await self._list_voices()
        locales = sorted({v["Locale"] for v in voices})

        embed = create_embed(
            title=self._i18n(interaction, "tts_languages_title"),
            description=self._i18n(interaction, "tts_languages_description"),
        )
        embed.add_field(
            name="Languages",
            value=", ".join(locales[:50]) or "N/A",
            inline=False,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="tts_setlanguage",
        description="ตั้งค่าภาษา TTS เริ่มต้นของเซิร์ฟเวอร์ / Set default TTS language",
    )
    @app_commands.describe(language="ภาษา เช่น th-TH, en-US, ja-JP")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def tts_setlanguage(
        self,
        interaction: discord.Interaction,
        language: str,
    ) -> None:
        voices = await self._voices_for_language(language)
        if not voices:
            await interaction.response.send_message(
                self._i18n(interaction, "tts_language_invalid", languages=language),
                ephemeral=True,
            )
            return

        guild_id = interaction.guild.id if interaction.guild else 0
        self.bot.guild_settings.set_tts_language(guild_id, language)

        embed = create_embed(
            title=self._i18n(interaction, "tts_setlanguage_title"),
            description=self._i18n(
                interaction, "tts_setlanguage_success", language=language
            ),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="tts_setvoice",
        description="ตั้งค่าโมเดลเสียง TTS เริ่มต้น / Set default TTS voice",
    )
    @app_commands.describe(
        voice_model="ชื่อเต็มของโมเดลเสียง เช่น th-TH-PremwadeeNeural"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def tts_setvoice(
        self,
        interaction: discord.Interaction,
        voice_model: str,
    ) -> None:
        voices = await self._list_voices()
        matched = next(
            (v for v in voices if v["ShortName"].lower() == voice_model.lower()),
            None,
        )
        if matched is None:
            await interaction.response.send_message(
                self._i18n(interaction, "tts_voice_invalid", voice=voice_model),
                ephemeral=True,
            )
            return

        guild_id = interaction.guild.id if interaction.guild else 0
        self.bot.guild_settings.set_tts_voice(guild_id, matched["ShortName"])
        language = _language_from_voice(matched["ShortName"])
        self.bot.guild_settings.set_tts_language(guild_id, language)

        embed = create_embed(
            title=self._i18n(interaction, "tts_setvoice_title"),
            description=self._i18n(
                interaction,
                "tts_setvoice_success",
                voice=matched["ShortName"],
                language=language,
            ),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TTS(bot))
