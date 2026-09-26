from __future__ import annotations

import discord

from discord import app_commands
from discord.ext import commands

from ..utils.embeds import make_embed


class FormulaCog(
    commands.Cog
):

    def __init__(
        self,
        bot,
    ):

        self.bot = bot

    # ==================================================
    # FORMULA HELPER
    # ==================================================

    async def send_formula(
        self,
        interaction: discord.Interaction,
        category: str,
        category_name: str,
    ):

        cheatsheet = (
            self.bot
            .formula_service
            .get_cheatsheet(
                category
            )
        )

        if not cheatsheet:

            await interaction.response.send_message(
                f"No {category_name.lower()} "
                "cheatsheet was found.",
                ephemeral=True,
            )

            return

        title = cheatsheet.get(
            "title",
            category_name,
        )

        formulas = cheatsheet.get(
            "formulas",
            [],
        )

        if not formulas:

            await interaction.response.send_message(
                f"No formulas were found in "
                f"the {category_name.lower()} cheatsheet.",
                ephemeral=True,
            )

            return

        embed = make_embed(
            title,
            "",
        )

        for item in formulas:

            name = item.get(
                "name",
                "Formula",
            )

            formula = item.get(
                "formula",
                "",
            )

            if not formula:
                continue

            embed.add_field(
                name=name,
                value=f"`{formula}`",
                inline=False,
            )

        embed.set_footer(
            text=(
                f"Mathdyl Academy • "
                f"{category_name} Cheatsheet"
            )
        )

        await interaction.response.send_message(
            embed=embed
        )

    # ==================================================
    # /limit_formula
    # ==================================================

    @app_commands.command(
        name="limit_formula",
        description="Get the limit formula cheatsheet.",
    )
    async def limit_formula(
        self,
        interaction: discord.Interaction,
    ):

        await self.send_formula(
            interaction,
            "limits",
            "Limit Formula",
        )

    # ==================================================
    # /derivative_formula
    # ==================================================

    @app_commands.command(
        name="derivative_formula",
        description="Get the derivative formula cheatsheet.",
    )
    async def derivative_formula(
        self,
        interaction: discord.Interaction,
    ):

        await self.send_formula(
            interaction,
            "derivatives",
            "Derivative Formula",
        )

    # ==================================================
    # /integral_formula
    # ==================================================

    @app_commands.command(
        name="integral_formula",
        description="Get the integral formula cheatsheet.",
    )
    async def integral_formula(
        self,
        interaction: discord.Interaction,
    ):

        await self.send_formula(
            interaction,
            "integrals",
            "Integral Formula",
        )

    # ==================================================
    # /quadratic_formula
    # ==================================================

    @app_commands.command(
        name="quadratic_formula",
        description="Get the quadratic formula cheatsheet.",
    )
    async def quadratic_formula(
        self,
        interaction: discord.Interaction,
    ):

        await self.send_formula(
            interaction,
            "quadratic",
            "Quadratic Formula",
        )

    # ==================================================
    # /trigonometry
    # ==================================================

    @app_commands.command(
        name="trigonometry",
        description="Get the trigonometry formula cheatsheet.",
    )
    async def trigonometry(
        self,
        interaction: discord.Interaction,
    ):

        await self.send_formula(
            interaction,
            "trigonometry",
            "Trigonometry",
        )


async def setup(bot):

    await bot.add_cog(
        FormulaCog(bot)
    )