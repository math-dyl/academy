
from __future__ import annotations

import discord
from discord.ext import commands

from ..utils.embeds import make_embed


class DailyCog(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    # ==================================================
    # FORMULA OF THE DAY
    # ==================================================

    def get_formula_of_the_day(self):

        return self.bot.daily_service.formula_of_the_day()

    async def send_formula_of_the_day(
        self,
        channel: discord.TextChannel,
    ):

        item = self.get_formula_of_the_day()

        if not item:
            return False

        title = item.get(
            "title",
            item.get(
                "name",
                "Formula of the Day",
            ),
        )

        explanation = item.get(
            "explanation",
            item.get(
                "description",
                "",
            ),
        )

        formula = item.get(
            "formula",
            item.get(
                "expression",
                "",
            ),
        )

        if not formula:
            return False

        embed = make_embed(
            title,
            explanation,
        )

        # ==============================================
        # RENDER EQUATION AS IMAGE
        # ==============================================

        equation_renderer = (
            self.bot.equation_renderer
        )

        image_path = equation_renderer.render(
            formula
        )

        if image_path:

            filename = image_path.name

            file = discord.File(
                image_path,
                filename=filename,
            )

            embed.set_image(
                url=f"attachment://{filename}"
            )

            embed.set_footer(
                text="Mathdyl Academy • Formula of the Day"
            )

            await channel.send(
                embed=embed,
                file=file,
            )

        else:

            embed.add_field(
                name="Formula",
                value=f"`{formula}`",
                inline=False,
            )

            embed.set_footer(
                text="Mathdyl Academy • Formula of the Day"
            )

            await channel.send(
                embed=embed
            )

        return True

    # ==================================================
    # PROBLEM OF THE DAY
    # ==================================================

    def get_problem_of_the_day(self):

        return self.bot.daily_service.problem_of_the_day()

    async def send_problem_of_the_day(
        self,
        channel: discord.TextChannel,
    ):

        item = self.get_problem_of_the_day()

        if not item:
            return False

        title = item.get(
            "title",
            "Problem of the Day",
        )

        problem = item.get(
            "problem",
            item.get(
                "question",
                "",
            ),
        )

        if not problem:
            return False

        equation_renderer = (
            self.bot.equation_renderer
        )

        # ==============================================
        # RENDER ENTIRE PROBLEM AS IMAGE
        # ==============================================

        if equation_renderer.looks_like_equation(
            problem
        ):

            image_path = (
                equation_renderer.render_content(
                    problem
                )
            )

            if image_path:

                filename = image_path.name

                file = discord.File(
                    image_path,
                    filename=filename,
                )

                # Image already contains the problem.
                # Embed contains only title, image, footer.
                embed = make_embed(
                    title,
                    "",
                )

                embed.set_image(
                    url=f"attachment://{filename}"
                )

                embed.set_footer(
                    text="Mathdyl Academy • Problem of the Day"
                )

                await channel.send(
                    embed=embed,
                    file=file,
                )

                return True

        # ==============================================
        # NORMAL EMBED
        # ==============================================

        embed = make_embed(
            title,
            problem,
        )

        embed.set_footer(
            text="Mathdyl Academy • Problem of the Day"
        )

        await channel.send(
            embed=embed
        )

        return True

    # ==================================================
    # SOLUTION OF THE DAY
    # ==================================================

    def get_solution_of_the_day(self):

        return self.bot.daily_service.solution_of_the_day()

    async def send_solution_of_the_day(
        self,
        channel: discord.TextChannel,
    ):

        item = self.get_solution_of_the_day()

        if not item:
            return False

        title = item.get(
            "title",
            "Solution of the Day",
        )

        problem = item.get(
            "problem",
            "",
        )

        solution = item.get(
            "solution",
            "",
        )

        explanation = item.get(
            "explanation",
            "",
        )

        if not problem or not solution:
            return False

        equation_renderer = (
            self.bot.equation_renderer
        )

        # ==============================================
        # COMBINE COMPLETE CONTENT
        # ==============================================

        full_content = (
            f"{problem}\n\n"
            f"Answer:\n"
            f"{solution}"
        )

        if explanation:

            full_content += (
                f"\n\n"
                f"Explanation:\n"
                f"{explanation}"
            )

        # ==============================================
        # RENDER ENTIRE SOLUTION AS IMAGE
        # ==============================================

        if equation_renderer.looks_like_equation(
            full_content
        ):

            image_path = (
                equation_renderer.render_content(
                    full_content
                )
            )

            if image_path:

                filename = image_path.name

                file = discord.File(
                    image_path,
                    filename=filename,
                )

                # Image already contains the problem,
                # solution, and explanation.
                # Embed contains only title, image, footer.
                embed = make_embed(
                    title,
                    "",
                )

                embed.set_image(
                    url=f"attachment://{filename}"
                )

                embed.set_footer(
                    text="Mathdyl Academy • Solution of the Day"
                )

                await channel.send(
                    embed=embed,
                    file=file,
                )

                return True

        # ==============================================
        # NORMAL EMBED
        # ==============================================

        embed = make_embed(
            title,
            problem,
        )

        embed.add_field(
            name="Solution",
            value=str(solution),
            inline=False,
        )

        if explanation:

            embed.add_field(
                name="Explanation",
                value=str(explanation),
                inline=False,
            )

        embed.set_footer(
            text="Mathdyl Academy • Solution of the Day"
        )

        await channel.send(
            embed=embed
        )

        return True

    # ==================================================
    # TRIVIA OF THE DAY
    # ==================================================

    def get_trivia_of_the_day(self):

        return self.bot.daily_service.trivia_of_the_day()

    async def send_trivia(
        self,
        channel: discord.TextChannel,
    ):

        item = self.get_trivia_of_the_day()

        if not item:
            return False

        question = item.get(
            "question",
            "",
        )

        answer = item.get(
            "answer",
            "",
        )

        explanation = item.get(
            "explanation",
            "",
        )

        if not question:
            return False

        equation_renderer = (
            self.bot.equation_renderer
        )

        # ==============================================
        # COMBINE COMPLETE CONTENT
        # ==============================================

        full_content = question

        if answer:

            full_content += (
                f"\n\n"
                f"Answer:\n"
                f"{answer}"
            )

        if explanation:

            full_content += (
                f"\n\n"
                f"Explanation:\n"
                f"{explanation}"
            )

        # ==============================================
        # RENDER ENTIRE TRIVIA AS IMAGE
        # ==============================================

        if equation_renderer.looks_like_equation(
            full_content
        ):

            image_path = (
                equation_renderer.render_content(
                    full_content
                )
            )

            if image_path:

                filename = image_path.name

                file = discord.File(
                    image_path,
                    filename=filename,
                )

                # Image already contains the question,
                # answer, and explanation.
                # Embed contains only title, image, footer.
                embed = make_embed(
                    "Math Trivia",
                    "",
                )

                embed.set_image(
                    url=f"attachment://{filename}"
                )

                embed.set_footer(
                    text="Mathdyl Academy • Math Trivia"
                )

                await channel.send(
                    embed=embed,
                    file=file,
                )

                return True

        # ==============================================
        # NORMAL EMBED
        # ==============================================

        embed = make_embed(
            "Math Trivia",
            question,
        )

        if answer:

            embed.add_field(
                name="Answer",
                value=str(answer),
                inline=False,
            )

        if explanation:

            embed.add_field(
                name="Explanation",
                value=str(explanation),
                inline=False,
            )

        embed.set_footer(
            text="Mathdyl Academy • Math Trivia"
        )

        await channel.send(
            embed=embed
        )

        return True


# ==================================================
# SETUP
# ==================================================

async def setup(bot):

    await bot.add_cog(
        DailyCog(bot)
    )

