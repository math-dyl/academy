from __future__ import annotations

import discord

from discord import app_commands
from discord.ext import commands

from ..utils.embeds import make_embed


class GeneralCog(commands.Cog):

    def __init__(self, bot):

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

        # ==============================================
        # QUICK ACCESS
        # ==============================================

        embed.add_field(
            name="Quick Access",
            value=(
                "`/limit_formula` — Limit formulas\n"
                "`/derivative_formula` — Derivative formulas\n"
                "`/integral_formula` — Integral formulas\n"
                "`/quadratic_formula` — Quadratic formula\n"
                "`/trigonometry` — Trigonometric formulas\n"
                "`/ask` — Ask the AI Math Assistant "
                "(3/day)"
            ),
            inline=False,
        )

        # ==============================================
        # COURSES
        # ==============================================

        embed.add_field(
            name="Courses",
            value=(
                "`/courses` — View available courses"
            ),
            inline=False,
        )

        # ==============================================
        # LEARNING
        # ==============================================

        embed.add_field(
            name="Learning",
            value=(
                "Open an available course channel "
                "and select **Start Learning** to "
                "begin a topic."
            ),
            inline=False,
        )

        # ==============================================
        # DAILY CONTENT
        # ==============================================

        embed.add_field(
            name="Daily Content",
            value=(
                "**Formula of the Day**\n"
                "**Problem of the Day**\n"
                "**Math Trivia**\n\n"
                "Daily content is automatically posted "
                "according to the Mathdyl schedule."
            ),
            inline=False,
        )

        embed.set_footer(
            text="Mathdyl Academy"
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )


async def setup(bot):

    await bot.add_cog(
        GeneralCog(bot)
    )