from __future__ import annotations

import discord

from discord import app_commands
from discord.ext import commands

from ..utils.embeds import make_embed


class CourseCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ==================================================
    # /courses
    # ==================================================

    @app_commands.command(
        name="courses",
        description="View all available courses.",
    )
    async def courses(
        self,
        interaction: discord.Interaction,
    ):

        courses = (
            self.bot
            .course_service
            .courses()
        )

        if not courses:

            await interaction.response.send_message(
                "No courses are currently available.",
                ephemeral=True,
            )

            return

        description = "\n".join(
            f"📚 `{course}`"
            for course in courses
        )

        embed = make_embed(
            "Available Courses",
            (
                "Here are the courses currently "
                "available in Mathdyl Academy.\n\n"
                f"{description}\n\n"
                "Go to the corresponding course channel "
                "to start learning."
            ),
        )

        embed.set_footer(
            text="Mathdyl Academy • Available Courses"
        )

        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot):

    await bot.add_cog(
        CourseCog(bot)
    )


# ======================================================
# LESSON VIEW
# ======================================================

class LessonView(
    discord.ui.View
):

    def __init__(
        self,
        bot,
        course,
        topic,
        lessons,
    ):

        super().__init__(
            timeout=900
        )

        self.bot = bot

        self.course = course
        self.topic = topic

        self.lessons = lessons

        self.index = 0

        self.update_buttons()

    # ==================================================
    # CURRENT LESSON
    # ==================================================

    @property
    def current(self):

        return self.lessons[
            self.index
        ]

    # ==================================================
    # EMBED
    # ==================================================

    def make_embed(self):

        lesson = self.current

        title = lesson.get(
            "title",
            f"Lesson {self.index + 1}",
        )

        content = lesson.get(
            "content",
            lesson.get(
                "description",
                "",
            ),
        )

        embed = make_embed(
            title,
            content,
        )

        formula = lesson.get(
            "formula"
        )

        if formula:

            embed.add_field(
                name="Formula",
                value=f"`{formula}`",
                inline=False,
            )

        example = lesson.get(
            "example"
        )

        if example:

            embed.add_field(
                name="Example",
                value=str(example),
                inline=False,
            )

        # ==============================================
        # FINAL LESSON
        # ==============================================

        if self.index == len(
            self.lessons
        ) - 1:

            embed.add_field(
                name="Lesson Complete",
                value=(
                    "You have completed all lessons "
                    "for this topic.\n\n"
                    "Choose **Practice** to reinforce "
                    "what you learned, or **Quiz** to "
                    "test your understanding."
                ),
                inline=False,
            )

        embed.set_footer(
            text=(
                f"{self.course} / "
                f"{self.topic} • "
                f"Lesson {self.index + 1}/"
                f"{len(self.lessons)}"
            )
        )

        return embed

    # ==================================================
    # BUTTONS
    # ==================================================

    def update_buttons(self):

        self.clear_items()

        # ==============================================
        # PREVIOUS
        # ==============================================

        previous = discord.ui.Button(
            label="Previous",
            style=discord.ButtonStyle.secondary,
            disabled=self.index == 0,
        )

        previous.callback = (
            self.previous_callback
        )

        self.add_item(
            previous
        )

        # ==============================================
        # NEXT
        # ==============================================

        next_button = discord.ui.Button(
            label="Next",
            style=discord.ButtonStyle.primary,
            disabled=(
                self.index >= len(self.lessons) - 1
            ),
        )

        next_button.callback = (
            self.next_callback
        )

        self.add_item(
            next_button
        )

        # ==============================================
        # PRACTICE / QUIZ
        # ==============================================

        if self.index == len(
            self.lessons
        ) - 1:

            practice = discord.ui.Button(
                label="Practice",
                style=discord.ButtonStyle.success,
            )

            quiz = discord.ui.Button(
                label="Quiz",
                style=discord.ButtonStyle.primary,
            )

            practice.callback = (
                self.practice_callback
            )

            quiz.callback = (
                self.quiz_callback
            )

            self.add_item(
                practice
            )

            self.add_item(
                quiz
            )

        # ==============================================
        # CLOSE
        # ==============================================

        close = discord.ui.Button(
            label="Close",
            style=discord.ButtonStyle.danger,
        )

        close.callback = (
            self.close_callback
        )

        self.add_item(
            close
        )

    # ==================================================
    # PREVIOUS
    # ==================================================

    async def previous_callback(
        self,
        interaction: discord.Interaction,
    ):

        if self.index > 0:
            self.index -= 1

        self.update_buttons()

        await interaction.response.edit_message(
            embed=self.make_embed(),
            view=self,
        )

    # ==================================================
    # NEXT
    # ==================================================

    async def next_callback(
        self,
        interaction: discord.Interaction,
    ):

        if self.index < len(
            self.lessons
        ) - 1:

            self.index += 1

        self.update_buttons()

        await interaction.response.edit_message(
            embed=self.make_embed(),
            view=self,
        )

    # ==================================================
    # PRACTICE
    # ==================================================

    async def practice_callback(
        self,
        interaction: discord.Interaction,
    ):

        questions = (
            self.bot
            .practice_service
            .questions(
                self.course,
                self.topic,
            )
        )

        if not questions:

            await interaction.response.send_message(
                "No practice questions were found "
                "for this topic.",
                ephemeral=True,
            )

            return

        from .practice import PracticeView

        view = PracticeView(
            bot=self.bot,
            course=self.course,
            topic=self.topic,
            questions=questions,
        )

        await interaction.response.send_message(
            embed=view.make_embed(),
            view=view,
            ephemeral=True,
        )

    # ==================================================
    # QUIZ
    # ==================================================

    async def quiz_callback(
        self,
        interaction: discord.Interaction,
    ):

        questions = (
            self.bot
            .quiz_service
            .questions(
                self.course,
                self.topic,
            )
        )

        if not questions:

            await interaction.response.send_message(
                "No quiz questions were found "
                "for this topic.",
                ephemeral=True,
            )

            return

        from .quizzes import QuizView

        view = QuizView(
            bot=self.bot,
            course=self.course,
            topic=self.topic,
            questions=questions,
        )

        await interaction.response.send_message(
            embed=view.make_embed(),
            view=view,
            ephemeral=True,
        )

    # ==================================================
    # CLOSE
    # ==================================================

    async def close_callback(
        self,
        interaction: discord.Interaction,
    ):

        self.clear_items()

        await interaction.response.edit_message(
            content="Learning session closed.",
            embed=None,
            view=self,
        )