from __future__ import annotations

import discord

from discord import app_commands

from discord.ext import commands

from ..utils.embeds import make_embed


class DailyCog(
    commands.Cog
):

    def __init__(
        self,
        bot,
    ):

        self.bot = bot

    @app_commands.command(
        name="formula_of_the_day",
        description="Show the formula of the day.",
    )
    async def formula_of_the_day(
        self,
        interaction: discord.Interaction,
    ):

        item = (
            self.bot
            .daily_service
            .formula_of_the_day()
        )

        if not item:

            await interaction.response.send_message(
                "No formula of the day was found.",
                ephemeral=True,
            )

            return

        embed = make_embed(
            item.get(
                "title",
                item.get(
                    "name",
                    "Formula of the Day",
                ),
            ),
            item.get(
                "explanation",
                item.get(
                    "description",
                    "",
                ),
            ),
        )

        embed.add_field(
            name="Formula",
            value=f"`{item.get('formula', '')}`",
            inline=False,
        )

        await interaction.response.send_message(
            embed=embed
        )

    @app_commands.command(
        name="problem_of_the_day",
        description="Show the problem of the day.",
    )
    async def problem_of_the_day(
        self,
        interaction: discord.Interaction,
    ):

        item = (
            self.bot
            .daily_service
            .problem_of_the_day()
        )

        if not item:

            await interaction.response.send_message(
                "No problem of the day was found.",
                ephemeral=True,
            )

            return

        embed = make_embed(
            item.get(
                "title",
                "Problem of the Day",
            ),
            item.get(
                "question",
                item.get(
                    "problem",
                    "",
                ),
            ),
        )

        solution = item.get(
            "solution",
            item.get(
                "answer",
                "",
            ),
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
        DailyCog(bot)
    )