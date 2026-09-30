from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from ..utils.embeds import make_embed

from ..services.equation_service import EquationService


class FormulaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.equation_service = EquationService()

    async def send_formula(
        self,
        interaction: discord.Interaction,
        category: str,
        category_name: str,
    ):
        cheatsheet = self.bot.formula_service.get_cheatsheet(category)

        if not cheatsheet:
            await interaction.response.send_message(
                f"No {category_name.lower()} cheatsheet was found.",
                ephemeral=True,
            )
            return

        title = cheatsheet.get("title", category_name)
        formulas = cheatsheet.get("formulas", [])

        if not formulas:
            await interaction.response.send_message(
                f"No formulas were found in the {category_name.lower()} cheatsheet.",
                ephemeral=True,
            )
            return

        # --------------------------------------------------
        # Prepare formulas
        # --------------------------------------------------

        formula_blocks = []

        for item in formulas:
            name = item.get("name", "Formula")
            formula = item.get("formula", "").strip()

            if not formula:
                continue

            formula_blocks.append(
                {
                    "name": name,
                    "formula": formula,
                }
            )

        if not formula_blocks:
            await interaction.response.send_message(
                f"No valid formulas were found in the {category_name.lower()} cheatsheet.",
                ephemeral=True,
            )
            return

        try:
            # --------------------------------------------------
            # Render complete cheatsheet as ONE image
            # --------------------------------------------------

            image = self.equation_service.render_formula_cheatsheet(
                title=title,
                formulas=formula_blocks,
            )

            filename = f"{category}_formulas.png"

            file = discord.File(
                image,
                filename=filename,
            )

            # --------------------------------------------------
            # Embed
            # --------------------------------------------------

            embed = make_embed(
                title,
                "",
            )

            embed.set_image(
                url=f"attachment://{filename}"
            )

            embed.set_footer(
                text=f"Mathdyl Academy • {category_name} Cheatsheet"
            )

            await interaction.response.send_message(
                embed=embed,
                file=file,
            )

        except Exception as error:
            # Keep the command from completely failing
            await interaction.response.send_message(
                f"Failed to render the {category_name.lower()} cheatsheet.",
                ephemeral=True,
            )

            print(
                f"[FormulaCog] Failed to render {category}: {error}"
            )

    # ==================================================
    # COMMANDS
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
    await bot.add_cog(FormulaCog(bot))