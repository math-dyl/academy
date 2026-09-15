from __future__ import annotations

import discord

from discord import app_commands
from discord.ext import commands

from ..utils.embeds import make_embed


class GeneralCog(
    commands.Cog
):

    def __init__(
        self,
        bot,
    ):

        self.bot = bot

    # ==================================================
    # /help
    # ==================================================

    @app_commands.command(
        name="help",
        description="Show Mathdyl Academy commands.",
    )
    async def help_command(
        self,
        interaction: discord.Interaction,
    ):

        embed = make_embed(
            "Mathdyl Academy",
            (
                "Self-paced mathematics "
                "learning through Discord."
            ),
        )

        embed.add_field(
            name="Courses",
            value=(
                "`/courses`\n"
                "`/course <course>`\n"
                "`/topics <course>`\n"
                "`/topic <course> <topic>`"
            ),
            inline=False,
        )

        embed.add_field(
            name="Learning",
            value=(
                "`/learn <course> <topic>`\n"
                "`/quiz <course> <topic>`"
            ),
            inline=False,
        )

        embed.add_field(
            name="General",
            value=(
                "`/formula`\n"
                "`/formula_of_the_day`\n"
                "`/problem`\n"
                "`/problem_of_the_day`\n"
                "`/ask <question>`"
            ),
            inline=False,
        )

        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot):

    await bot.add_cog(
        GeneralCog(bot)
    )