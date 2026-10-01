from __future__ import annotations

import asyncio
import logging

import discord

from discord import app_commands
from discord.ext import commands

from ..utils.embeds import make_embed

logger = logging.getLogger(__name__)


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

        courses = self.bot.course_service.courses()

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
# LESSON / CONTENT VIEW
# ======================================================

class LessonView(discord.ui.View):

    def __init__(
        self,
        bot,
        course,
        topic,
        lessons,
        user_id: int,
        start_index: int = 0,
    ):

        super().__init__(
            timeout=900
        )

        self.bot = bot
        self.user_id = user_id
        self._progress_lock = asyncio.Lock()
        self.course = course
        self.topic = topic

        # Contains all content blocks:
        #
        # lesson
        # example
        # concept_check
        #
        self.lessons = lessons

        self.index = max(0, min(int(start_index), len(lessons) - 1))

        # Concept-check state
        self.concept_answered = False
        self.selected_answer = None

        self.update_buttons()

    async def _check_owner(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user_id:
            return True
        await interaction.response.send_message(
            "This learning session belongs to another user.",
            ephemeral=True,
        )
        return False

    async def _save_position(self, index: int) -> bool:
        try:
            await self.bot.database_service.save_course_progress(
                self.user_id, self.course, self.topic, index
            )
            return True
        except Exception:
            logger.exception("Could not persist lesson position.")
            return False

    async def _move(self, interaction: discord.Interaction, offset: int) -> None:
        async with self._progress_lock:
            new_index = max(0, min(self.index + offset, len(self.lessons) - 1))
            if not await self._save_position(new_index):
                await interaction.followup.send(
                    "I couldn't save your progress, so I kept you at the current item. Please try again.",
                    ephemeral=True,
                )
                return
            self.index = new_index
            self.concept_answered = False
            self.selected_answer = None
            self.update_buttons()
            await interaction.edit_original_response(
                embed=self.make_embed(),
                view=self,
            )

    # ==================================================
    # CURRENT CONTENT
    # ==================================================

    @property
    def current(self):

        if not self.lessons:
            return {}

        return self.lessons[
            self.index
        ]

    # ==================================================
    # EMBED
    # ==================================================

    def make_embed(self):

        item = self.current

        item_type = item.get(
            "type",
            "lesson",
        )

        if item_type == "lesson":

            return self.make_lesson_embed(
                item
            )

        if item_type == "example":

            return self.make_example_embed(
                item
            )

        if item_type == "concept_check":

            return self.make_concept_check_embed(
                item
            )

        return make_embed(
            item.get(
                "title",
                "Content",
            ),
            item.get(
                "content",
                "No content available.",
            ),
        )

    # ==================================================
    # LESSON EMBED
    # ==================================================

    def make_lesson_embed(
        self,
        lesson,
    ):

        title = lesson.get(
            "title",
            "Lesson",
        )

        content = lesson.get(
            "content",
            "",
        )

        embed = make_embed(
            title,
            content,
        )

        key_terms = lesson.get(
            "key_terms"
            )

        if key_terms:

            embed.add_field(
                name="Key Terms",
                value=key_terms,
                inline=False,
            )

        # Formula is optional.
        formula = lesson.get(
            "formula"
        )

        if formula:

            embed.add_field(
                name="Formula",
                value=f"`{formula}`",
                inline=False,
            )
            

        examples = lesson.get(
            "examples"
        )

        if examples:

            embed.add_field(
                name="Examples",
                value=f"```text\n{examples}\n```",
                inline=False,
            )

        self.add_footer(
            embed
        )

        return embed

    # ==================================================
    # EXAMPLE EMBED
    # ==================================================

    def make_example_embed(
        self,
        example,
    ):

        title = example.get(
            "title",
            "Example",
        )

        embed = make_embed(
            title,
            "",
        )

        question = example.get(
            "question"
        )

        if question:

            embed.add_field(
                name="Question",
                value=question,
                inline=False,
            )

        content = example.get(
            "content"
        )

        if content:

            embed.add_field(
                name="Example",
                value=content,
                inline=False,
            )

        solution = example.get(
            "solution"
        )

        if solution:

            embed.add_field(
                name="Solution",
                value=solution,
                inline=False,
            )

        answer = example.get(
            "answer"
        )

        if answer:

            embed.add_field(
                name="Answer",
                value=answer,
                inline=False,
            )

        self.add_footer(
            embed
        )

        return embed

    # ==================================================
    # CONCEPT CHECK EMBED
    # ==================================================

    def make_concept_check_embed(
        self,
        concept_check,
    ):

        question = concept_check.get(
            "question",
            "Concept Check",
        )

        embed = make_embed(
            "Concept Check",
            question,
        )

        options = concept_check.get(
            "options",
            [],
        )

        # ==================================================
        # BEFORE ANSWER
        # ==================================================

        if not self.concept_answered:

            if options:

                option_text = "\n".join(
                    f"**{option.get('id', '')}.** "
                    f"{option.get('text', '')}"
                    for option in options
                )

                embed.add_field(
                    name="Choose an answer",
                    value=option_text,
                    inline=False,
                )

        # ==================================================
        # AFTER ANSWER
        # ==================================================

        else:

            correct_answer = concept_check.get(
                "correct_answer"
            )

            selected_answer = self.selected_answer

            # --------------------------------------------------
            # Find selected option
            # --------------------------------------------------

            selected_option = next(
                (
                    option
                    for option in options
                    if option.get("id")
                    == selected_answer
                ),
                None,
            )

            selected_text = (
                selected_option.get("text")
                if selected_option
                else str(selected_answer)
            )

            # --------------------------------------------------
            # Find correct option
            # --------------------------------------------------

            correct_option = next(
                (
                    option
                    for option in options
                    if option.get("id")
                    == correct_answer
                ),
                None,
            )

            correct_text = (
                correct_option.get("text")
                if correct_option
                else str(correct_answer)
            )

            # --------------------------------------------------
            # Determine result
            # --------------------------------------------------

            is_correct = (
                selected_answer
                == correct_answer
            )

            if is_correct:

                embed.add_field(
                    name="Result",
                    value="✅ **Correct!**",
                    inline=False,
                )

            else:

                embed.add_field(
                    name="Result",
                    value="❌ **Not quite.**",
                    inline=False,
                )

            # --------------------------------------------------
            # Your Answer
            # --------------------------------------------------

            embed.add_field(
                name="Your Answer",
                value=(
                    f"**{selected_answer}.** "
                    f"{selected_text}"
                ),
                inline=False,
            )

            # --------------------------------------------------
            # Correct Answer
            # --------------------------------------------------

            embed.add_field(
                name="Correct Answer",
                value=(
                    f"**{correct_answer}.** "
                    f"{correct_text}"
                ),
                inline=False,
            )

            # --------------------------------------------------
            # Explanation
            # --------------------------------------------------

            explanation = concept_check.get(
                "explanation"
            )

            if explanation:

                embed.add_field(
                    name="Explanation",
                    value=explanation,
                    inline=False,
                )

        self.add_footer(
            embed
        )

        return embed

    # ==================================================
    # FOOTER
    # ==================================================

    def add_footer(
        self,
        embed,
    ):

        item = self.current

        item_type = item.get(
            "type",
            "lesson",
        )

        type_name = {
            "lesson": "Lesson",
            "example": "Example",
            "concept_check": "Concept Check",
        }.get(
            item_type,
            "Content",
        )

        embed.set_footer(
            text=(
                f"{self.course} / "
                f"{self.topic} • "
                f"{type_name} "
                f"{self.index + 1}/"
                f"{len(self.lessons)}"
            )
        )

    # ==================================================
    # BUTTONS
    # ==================================================

    def update_buttons(self):

        self.clear_items()

        item = self.current

        item_type = item.get(
            "type",
            "lesson",
        )

        # ==================================================
        # CONCEPT CHECK ANSWERS
        # ==================================================

        if (
            item_type == "concept_check"
            and not self.concept_answered
        ):

            options = item.get(
                "options",
                [],
            )

            for option in options:

                answer_id = option.get(
                    "id"
                )

                if not answer_id:
                    continue

                button = discord.ui.Button(
                    label=answer_id,
                    style=discord.ButtonStyle.primary,
                    row=0,
                )

                async def callback(
                    interaction: discord.Interaction,
                    answer_id=answer_id,
                ):

                    await self.answer_concept_check(
                        interaction,
                        answer_id,
                    )

                button.callback = callback

                self.add_item(
                    button
                )

        # ==================================================
        # PREVIOUS
        # ==================================================

        previous = discord.ui.Button(
            label="Previous",
            style=discord.ButtonStyle.secondary,
            disabled=(
                self.index == 0
            ),
            row=1,
        )

        previous.callback = (
            self.previous_callback
        )

        self.add_item(
            previous
        )

        # ==================================================
        # NEXT
        # ==================================================

        # Don't allow the user to skip an unanswered
        # concept check.

        concept_check_locked = (
            item_type == "concept_check"
            and not self.concept_answered
        )

        next_button = discord.ui.Button(
            label="Next",
            style=discord.ButtonStyle.primary,
            disabled=(
                self.index >= len(self.lessons) - 1
                or concept_check_locked
            ),
            row=1,
        )

        next_button.callback = (
            self.next_callback
        )

        self.add_item(
            next_button
        )

        # ==================================================
        # FINAL CONTENT
        # ==================================================

        if self.index == len(
            self.lessons
        ) - 1:

            practice = discord.ui.Button(
                label="Practice",
                style=discord.ButtonStyle.primary,
                row=2,
            )

            quiz = discord.ui.Button(
                label="Quiz",
                style=discord.ButtonStyle.success,
                row=2,
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

        # ==================================================
        # CLOSE
        # ==================================================

        close = discord.ui.Button(
            label="Close",
            style=discord.ButtonStyle.danger,
            row=1,
        )

        close.callback = (
            self.close_callback
        )

        self.add_item(
            close
        )

    # ==================================================
    # CONCEPT CHECK ANSWER
    # ==================================================

    async def answer_concept_check(
        self,
        interaction: discord.Interaction,
        answer: str,
    ):
        if not await self._check_owner(interaction):
            return

        item = self.current

        # ==================================================
        # SAFETY CHECK
        # ==================================================

        if item.get("type") != "concept_check":

            await interaction.response.send_message(
                "This is not a concept check.",
                ephemeral=True,
            )

            return

        # ==================================================
        # PREVENT DOUBLE ANSWER
        # ==================================================

        if self.concept_answered:

            await interaction.response.send_message(
                "You have already answered this "
                "concept check.",
                ephemeral=True,
            )

            return

        # ==================================================
        # ACKNOWLEDGE INTERACTION FIRST
        # ==================================================

        await interaction.response.defer()

        # ==================================================
        # SAVE ANSWER
        # ==================================================

        self.selected_answer = answer
        self.concept_answered = True

        # ==================================================
        # UPDATE BUTTONS
        # ==================================================

        self.update_buttons()

        # ==================================================
        # UPDATE ORIGINAL MESSAGE
        # ==================================================

        await interaction.edit_original_response(
            embed=self.make_embed(),
            view=self,
        )

    # ==================================================
    # PREVIOUS
    # ==================================================

    async def previous_callback(self, interaction: discord.Interaction):
        if not await self._check_owner(interaction):
            return
        await interaction.response.defer()
        await self._move(interaction, -1)

    # ==================================================
    # NEXT
    # ==================================================

    async def next_callback(self, interaction: discord.Interaction):
        if not await self._check_owner(interaction):
            return
        item = self.current
        if item.get("type") == "concept_check" and not self.concept_answered:
            await interaction.response.send_message("Please answer the concept check before continuing.", ephemeral=True)
            return
        await interaction.response.defer()
        await self._move(interaction, 1)

    # ==================================================
    # PRACTICE
    # ==================================================

    async def practice_callback(self, interaction: discord.Interaction):
        if not await self._check_owner(interaction):
            return
        if not await self._save_position(self.index):
            await interaction.response.send_message("I couldn't save your progress right now. Please try again shortly.", ephemeral=True)
            return
        questions = self.bot.practice_service.questions(self.course, self.topic)
        if not questions:
            await interaction.response.send_message("No practice questions were found for this topic.", ephemeral=True)
            return
        from .practice import PracticeView
        view = PracticeView(bot=self.bot, course=self.course, topic=self.topic, questions=questions)
        await interaction.response.send_message(embed=view.make_embed(), view=view, ephemeral=True)

    # ==================================================
    # QUIZ
    # ==================================================

    async def quiz_callback(self, interaction: discord.Interaction):
        if not await self._check_owner(interaction):
            return
        if not await self._save_position(self.index):
            await interaction.response.send_message("I couldn't save your progress right now. Please try again shortly.", ephemeral=True)
            return
        questions = self.bot.quiz_service.questions(self.course, self.topic)
        if not questions:
            await interaction.response.send_message("No quiz questions were found for this topic.", ephemeral=True)
            return
        from .quizzes import QuizView
        view = QuizView(
            bot=self.bot,
            course=self.course,
            topic=self.topic,
            questions=questions,
            user_id=interaction.user.id,
            lesson_index=self.index,
        )
        await interaction.response.send_message(embed=view.make_embed(), view=view, ephemeral=True)

    # ==================================================
    # CLOSE
    # ==================================================

    async def close_callback(self, interaction: discord.Interaction):
        if not await self._check_owner(interaction):
            return
        await interaction.response.defer()
        self.stop()
        await interaction.edit_original_response(content="Learning session closed.", embed=None, view=None)

