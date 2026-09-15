from __future__ import annotations

import discord

from discord import app_commands

from discord.ext import commands

from ..utils.embeds import make_embed


class ProblemCog(
    commands.Cog
):

    def __init__(
        self,
        bot,
    ):

        self.bot = bot

    @app_commands.command(
        name="problem",
        description="Show a random mathematics problem.",
    )
    async def problem(
        self,
        interaction: discord.Interaction,
    ):

        item = (
            self.bot
            .problem_service
            .random()
        )

        if not item:

            await interaction.response.send_message(
                "No problems were found.",
                ephemeral=True,
            )

            return

        question = item.get(
            "question",
            item.get(
                "problem",
                "",
            ),
        )

        solution = item.get(
            "solution",
            item.get(
                "answer",
                "",
            ),
        )

        embed = make_embed(
            "Practice Problem",
            question,
        )

        if solution:

            embed.add_field(
                name="Solution",
                value=str(solution),
                inline=False,
            )

        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot):

    await bot.add_cog(
        ProblemCog(bot)
    )