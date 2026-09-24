from __future__ import annotations

import discord
from discord.ext import commands


class PracticeView(discord.ui.View):

    def __init__(
        self,
        bot: commands.Bot,
        course: str,
        topic: str,
        questions: list[dict],
    ):
        super().__init__(timeout=900)

        self.bot = bot
        self.course = course
        self.topic = topic
        self.questions = questions

        self.index = 0
        self.score = 0
        self.answered = False

        self.build_buttons()

    # ==================================================
    # CURRENT QUESTION
    # ==================================================

    def current_question(self) -> dict:
        return self.questions[self.index]

    # ==================================================
    # GET OPTIONS
    # ==================================================

    def get_options(self) -> list[str]:
        """
        Returns practice options as a list.

        Example:
        [
            "Natural numbers only",
            "Whole numbers",
            "Irrational numbers only",
            "None of the above"
        ]
        """

        options = self.current_question().get(
            "options",
            []
        )

        # Normal list format
        if isinstance(options, list):
            return [
                str(option)
                for option in options
            ]

        # Also support dictionary format
        # in case future JSON files use A/B/C/D.
        if isinstance(options, dict):
            return [
                str(options[letter])
                for letter in ["A", "B", "C", "D"]
                if letter in options
            ]

        return []

    # ==================================================
    # BUILD ANSWER BUTTONS
    # ==================================================

    def build_buttons(self):

        self.clear_items()

        options = self.get_options()

        letters = ["A", "B", "C", "D"]

        for index, option in enumerate(
            options[:4]
        ):

            button = AnswerButton(
                letter=letters[index],
                label=letters[index],
            )

            self.add_item(button)

    # ==================================================
    # EMBED
    # ==================================================

    def make_embed(self) -> discord.Embed:

        question = self.current_question()
        options = self.get_options()

        embed = discord.Embed(
            title=(
                f"📚 "
                f"{self.topic.replace('-', ' ').title()}"
            ),
            description=(
                f"**Practice • Question "
                f"{self.index + 1}/"
                f"{len(self.questions)}**\n\n"
                f"{question.get('question', '')}"
            ),
            color=0x2563EB,
        )

        letters = ["A", "B", "C", "D"]

        option_text = []

        for index, option in enumerate(
            options[:4]
        ):

            option_text.append(
                f"**{letters[index]}.** {option}"
            )

        if option_text:

            embed.add_field(
                name="Choices",
                value="\n".join(option_text),
                inline=False,
            )

        embed.set_footer(
            text="Select an answer below."
        )

        return embed

    # ==================================================
    # ANSWER
    # ==================================================

    async def answer(
        self,
        interaction: discord.Interaction,
        letter: str,
    ):

        if self.answered:

            await interaction.response.send_message(
                "You have already answered this question.",
                ephemeral=True,
            )

            return

        options = self.get_options()

        letters = ["A", "B", "C", "D"]

        try:

            option_index = letters.index(letter)

            selected_answer = options[
                option_index
            ]

        except (
            ValueError,
            IndexError,
        ):

            await interaction.response.send_message(
                "Invalid answer.",
                ephemeral=True,
            )

            return

        question = self.current_question()

        correct_answer = question.get(
            "answer",
            "",
        )

        is_correct = (
            selected_answer == correct_answer
        )

        self.answered = True

        if is_correct:

            self.score += 1

            result = "✅ **Correct!**"

        else:

            result = (
                "❌ **Incorrect!**\n\n"
                f"Correct answer: "
                f"**{correct_answer}**"
            )

        # ==================================================
        # DISABLE ANSWER BUTTONS
        # ==================================================

        for item in self.children:

            if isinstance(
                item,
                discord.ui.Button,
            ):

                item.disabled = True

        # ==================================================
        # RESULT EMBED
        # ==================================================

        explanation = question.get(
            "explanation"
        )

        description = result

        if explanation:

            description += (
                f"\n\n"
                f"**Explanation**\n"
                f"{explanation}"
            )

        embed = discord.Embed(
            title=(
                f"📚 "
                f"{self.topic.replace('-', ' ').title()} "
                f"— Practice"
            ),
            description=description,
            color=0x2563EB,
        )

        embed.add_field(
            name="Question",
            value=question.get(
                "question",
                "",
            ),
            inline=False,
        )

        # ==================================================
        # NEXT QUESTION
        # ==================================================

        if (
            self.index + 1
            < len(self.questions)
        ):

            next_button = discord.ui.Button(
                label="Next Question",
                style=discord.ButtonStyle.primary,
                custom_id=(
                    "mathdyl:practice:next"
                ),
            )

            async def next_callback(
                next_interaction: discord.Interaction,
            ):

                self.index += 1
                self.answered = False

                self.build_buttons()

                await next_interaction.response.edit_message(
                    embed=self.make_embed(),
                    view=self,
                )

            next_button.callback = next_callback

            self.add_item(
                next_button
            )

        else:

            finish_button = discord.ui.Button(
                label="Finish Practice",
                style=discord.ButtonStyle.primary,
                custom_id=(
                    "mathdyl:practice:finish"
                ),
            )

            async def finish_callback(
                finish_interaction: discord.Interaction,
            ):

                await self.finish_practice(
                    finish_interaction
                )

            finish_button.callback = (
                finish_callback
            )

            self.add_item(
                finish_button
            )

        await interaction.response.edit_message(
            embed=embed,
            view=self,
        )

    # ==================================================
    # FINISH PRACTICE
    # ==================================================

    async def finish_practice(
        self,
        interaction: discord.Interaction,
    ):

        total = len(
            self.questions
        )

        percentage = (
            (self.score / total) * 100
            if total
            else 0
        )

        embed = discord.Embed(
            title="🎯 Practice Complete",
            description=(
                f"**Score:** "
                f"{self.score}/{total}\n"
                f"**Percentage:** "
                f"{percentage:.0f}%"
            ),
            color=0x2563EB,
        )

        embed.add_field(
            name="Keep Learning!",
            value=(
                "Review the lesson and try the "
                "practice again to improve your score."
            ),
            inline=False,
        )

        self.clear_items()

        await interaction.response.edit_message(
            embed=embed,
            view=self,
        )


# ======================================================
# ANSWER BUTTON
# ======================================================

class AnswerButton(
    discord.ui.Button
):

    def __init__(
        self,
        letter: str,
        label: str,
    ):

        super().__init__(
            label=label,
            style=discord.ButtonStyle.primary,
            custom_id=(
                f"mathdyl:practice:answer:{letter}"
            ),
        )

        self.letter = letter

    async def callback(
        self,
        interaction: discord.Interaction,
    ):

        view = self.view

        if not isinstance(
            view,
            PracticeView,
        ):
            return

        await view.answer(
            interaction,
            self.letter,
        )