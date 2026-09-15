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

    @app_commands.command(
        name="formula",
        description="Show a random mathematics formula.",
    )
    async def formula(
        self,
        interaction: discord.Interaction,
    ):

        item = (
            self.bot
            .formula_service
            .random()
        )

        if not item:

            await interaction.response.send_message(
                "No formulas were found.",
                ephemeral=True,
            )

            return

        title = item.get(
            "name",
            item.get(
                "title",
                "Formula",
            ),
        )

        formula = item.get(
            "formula",
            item.get(
                "expression",
                "",
            ),
        )

        explanation = item.get(
            "explanation",
            item.get(
                "description",
                "",
            ),
        )

        embed = make_embed(
            title,
            explanation,
        )

        embed.add_field(
            name="Formula",
            value=f"`{formula}`",
            inline=False,
        )

        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot):

    await bot.add_cog(
        FormulaCog(bot)
    )