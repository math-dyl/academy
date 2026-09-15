from __future__ import annotations

import discord

from discord import app_commands
from discord.ext import commands

from ..utils.embeds import make_embed


class QuizzesCog(
    commands.Cog
):

    def __init__(
        self,
        bot,
    ):

        self.bot = bot

    # ==================================================
    # /quiz
    # ==================================================

    @app_commands.command(
        name="quiz",
        description="Start a quiz for a topic.",
    )
    @app_commands.describe(
        course="Course slug",
        topic="Topic slug",
    )
    async def quiz(
        self,
        interaction: discord.Interaction,
        course: str,
        topic: str,
    ):

        questions = (
            self.bot
            .quiz_service
            .questions(
                course,
                topic,
            )
        )

        if not questions:

            await interaction.response.send_message(
                "No quiz questions were found.",
                ephemeral=True,
            )

            return

        view = QuizView(
            bot=self.bot,
            course=course,
            topic=topic,
            questions=questions,
        )

        await interaction.response.send_message(
            embed=view.make_embed(),
            view=view,
            ephemeral=True,
        )


async def setup(bot):

    await bot.add_cog(
        QuizzesCog(bot)
    )


# ======================================================
# QUIZ VIEW
# ======================================================

class QuizView(
    discord.ui.View
):

    def __init__(
        self,
        bot,
        course,
        topic,
        questions,
    ):

        super().__init__(
            timeout=900
        )

        self.bot = bot

        self.course = course
        self.topic = topic

        self.questions = questions

        self.index = 0
        self.score = 0

        # Stores every answer.
        self.answers = []

        self.build_buttons()

    # ==================================================
    # CURRENT QUESTION
    # ==================================================

    @property
    def current(self):

        return self.questions[
            self.index
        ]

    # ==================================================
    # EMBED
    # ==================================================

    def make_embed(self):

        question = self.current

        text = question.get(
            "question",
            question.get(
                "problem",
                "",
            ),
        )

        embed = make_embed(
            (
                "Quiz • "
                f"Question {self.index + 1}/"
                f"{len(self.questions)}"
            ),
            text,
        )

        options = question.get(
            "options",
            [],
        )

        if options:

            letters = (
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            )

            choices = "\n".join(
                (
                    f"**{letters[i]}.** "
                    f"{option}"
                )
                for i, option in enumerate(
                    options
                )
            )

            embed.add_field(
                name="Choices",
                value=choices,
                inline=False,
            )

        embed.set_footer(
            text=(
                f"Score: {self.score} "
                f"• Select an answer below"
            )
        )

        return embed

    # ==================================================
    # BUILD BUTTONS
    # ==================================================

    def build_buttons(self):

        self.clear_items()

        options = self.current.get(
            "options",
            [],
        )

        if options:

            letters = (
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            )

            for index, option in enumerate(
                options[:4]
            ):

                button = AnswerButton(
                    label=letters[index],
                    value=str(option),
                    index=index,
                )

                self.add_item(
                    button
                )

        else:

            button = NextQuestionButton(
                label="Next Question",
                style=discord.ButtonStyle.primary,
            )

            self.add_item(
                button
            )

    # ==================================================
    # ANSWER
    # ==================================================

    async def answer(
        self,
        interaction: discord.Interaction,
        answer: str,
    ):

        question = self.current

        correct = (
            self.bot
            .quiz_service
            .check(
                question,
                answer,
            )
        )

        expected = question.get(
            "answer",
            question.get(
                "correct_answer",
                "unknown",
            ),
        )

        if correct:

            self.score += 1

            feedback = "Correct."

        else:

            feedback = (
                "Incorrect.\n"
                f"Correct answer: `{expected}`"
            )

        # ==============================================
        # STORE RESULT
        # ==============================================

        self.answers.append(
            {
                "user_answer": answer,
                "correct_answer": expected,
                "correct": correct,
            }
        )

        # ==============================================
        # NEXT QUESTION
        # ==============================================

        self.index += 1

        if self.index >= len(
            self.questions
        ):

            await self.finish_quiz(
                interaction,
                feedback,
            )

            return

        self.build_buttons()

        await interaction.response.edit_message(
            content=feedback,
            embed=self.make_embed(),
            view=self,
        )

    # ==================================================
    # FINISH QUIZ
    # ==================================================

    async def finish_quiz(
        self,
        interaction: discord.Interaction,
        feedback: str = "",
    ):

        self.clear_items()

        total = len(
            self.questions
        )

        percentage = (
            self.score / total * 100
            if total
            else 0
        )

        # ==============================================
        # COMPLETION EMBED
        # ==============================================

        embed = make_embed(
            "Quiz Complete",
            (
                f"{feedback}\n\n"
                f"Final Score: "
                f"**{self.score}/{total}**\n"
                f"Percentage: "
                f"**{percentage:.1f}%**\n\n"
                "Generating your quiz review PDF..."
            ),
        )

        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=self,
        )

        # ==============================================
        # GENERATE PDF
        # ==============================================

        try:

            pdf = (
                self.bot
                .pdf_service
                .create_quiz_pdf(
                    course=self.course,
                    topic=self.topic,
                    questions=self.questions,
                    answers=self.answers,
                    score=self.score,
                )
            )

            filename = (
                "quiz-review-"
                f"{self.course}-"
                f"{self.topic}.pdf"
            )

            file = discord.File(
                pdf,
                filename=filename,
            )

            # ==========================================
            # SEND PDF
            # ==========================================

            await interaction.followup.send(
                content=(
                    "Your **Quiz Review PDF** "
                    "is ready."
                ),
                file=file,
                ephemeral=True,
            )

        except Exception as error:

            await interaction.followup.send(
                content=(
                    "The quiz was completed, "
                    "but I could not generate "
                    "the review PDF.\n\n"
                    f"`{error}`"
                ),
                ephemeral=True,
            )


# ======================================================
# ANSWER BUTTON
# ======================================================

class AnswerButton(
    discord.ui.Button
):

    def __init__(
        self,
        label,
        value,
        index,
    ):

        super().__init__(
            label=label,
            style=discord.ButtonStyle.primary,
            custom_id=f"answer_{index}",
        )

        self.value = value

    async def callback(
        self,
        interaction: discord.Interaction,
    ):

        view: QuizView = self.view

        await view.answer(
            interaction,
            self.value,
        )


# ======================================================
# NEXT QUESTION BUTTON
# ======================================================

class NextQuestionButton(
    discord.ui.Button
):

    async def callback(
        self,
        interaction: discord.Interaction,
    ):

        view: QuizView = self.view

        question = view.current

        expected = question.get(
            "answer",
            question.get(
                "correct_answer",
                "Unknown",
            ),
        )

        view.answers.append(
            {
                "user_answer": "No answer",
                "correct_answer": expected,
                "correct": False,
            }
        )

        view.index += 1

        if view.index >= len(
            view.questions
        ):

            await view.finish_quiz(
                interaction
            )

            return

        view.build_buttons()

        await interaction.response.edit_message(
            embed=view.make_embed(),
            view=view,
        )