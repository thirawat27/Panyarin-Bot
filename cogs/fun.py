"""Entertainment and fun commands."""

import random

import discord
from discord import app_commands
from discord.ext import commands

from utils import I18n, create_embed

EIGHTBALL_RESPONSES = [
    "It is certain.",
    "It is decidedly so.",
    "Without a doubt.",
    "Yes definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook good.",
    "Yes.",
    "Signs point to yes.",
    "Reply hazy, try again.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
    "Don't count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful.",
]

THAI_EIGHTBALL_RESPONSES = [
    "แน่นอน",
    "แน่ใจได้เลย",
    "ไม่ต้องสงสัย",
    "ใช่แน่นอน",
    "คุณสามารถไว้วางใจได้",
    "ตามที่ฉันเห็น ใช่",
    "เป็นไปได้มาก",
    "แนวโน้มดี",
    "ใช่",
    "สัญญาณบ่งชี้ว่าใช่",
    "คำตอบคลุมเครือ ลองใหม่อีกครั้ง",
    "ถามอีกครั้งในภายหลัง",
    "ยังไม่ควรบอกคุณตอนนี้",
    "ยังคาดการณ์ไม่ได้",
    "ตั้งสมาธิแล้วถามอีกครั้ง",
    "อย่าหวังเลย",
    "คำตอบของฉันคือไม่",
    "แหล่งข้อมูลของฉันบอกว่าไม่",
    "แนวโน้มไม่ค่อยดี",
    "น่าสงสัยมาก",
]


class Fun(commands.Cog):
    """Fun and entertainment commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def _i18n(self, interaction: discord.Interaction, key: str, **kwargs) -> str:
        guild_id = interaction.guild.id if interaction.guild else 0
        lang = self.bot.guild_settings.get_language(guild_id)
        return I18n.translate(lang, key, **kwargs)

    @app_commands.command(name="dice", description="Roll a six-sided dice")
    @app_commands.describe(sides="Number of sides (default 6)")
    async def dice(
        self,
        interaction: discord.Interaction,
        sides: app_commands.Range[int, 2, 100] = 6,
    ) -> None:
        result = random.randint(1, sides)
        embed = create_embed(
            title=self._i18n(interaction, "dice_title"),
            description=self._i18n(interaction, "dice_result", result=result),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction) -> None:
        lang = self.bot.guild_settings.get_language(
            interaction.guild.id if interaction.guild else 0
        )
        heads = I18n.translate(lang, "coinflip_head")
        tails = I18n.translate(lang, "coinflip_tail")
        result = random.choice([heads, tails])
        embed = create_embed(
            title=self._i18n(interaction, "coinflip_title"),
            description=self._i18n(interaction, "coinflip_result", result=result),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="8ball", description="Ask the magic 8-ball")
    @app_commands.describe(question="Your question")
    async def eightball(self, interaction: discord.Interaction, question: str) -> None:
        lang = self.bot.guild_settings.get_language(
            interaction.guild.id if interaction.guild else 0
        )
        responses = THAI_EIGHTBALL_RESPONSES if lang == "th" else EIGHTBALL_RESPONSES
        answer = random.choice(responses)
        embed = create_embed(
            title=self._i18n(interaction, "eightball_title"),
            description=f"**Q:** {question}\n**A:** {answer}",
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="poll", description="Create a simple poll")
    @app_commands.describe(question="Poll question")
    async def poll(self, interaction: discord.Interaction, question: str) -> None:
        embed = create_embed(
            title=self._i18n(interaction, "poll_title"),
            description=f"{question}\n\nPoll by {interaction.user.mention}",
        )
        message = await interaction.channel.send(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("👎")
        await message.add_reaction("🤷")
        await interaction.response.send_message("Poll created!", ephemeral=True)

    @app_commands.command(name="ask", description="Ask a yes/no question")
    @app_commands.describe(question="Your question")
    async def ask(self, interaction: discord.Interaction, question: str) -> None:
        lang = self.bot.guild_settings.get_language(
            interaction.guild.id if interaction.guild else 0
        )
        responses = THAI_EIGHTBALL_RESPONSES if lang == "th" else EIGHTBALL_RESPONSES
        answer = random.choice(responses)
        embed = create_embed(
            title=self._i18n(interaction, "ask_title"),
            description=f"**Q:** {question}\n**A:** {answer}",
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
