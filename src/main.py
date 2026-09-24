from __future__ import annotations

import asyncio
import logging

import discord

from discord.ext import commands

from .services.ai_service import AIService
from .services.content_service import ContentService
from .services.course_service import CourseService
from .services.daily_service import DailyService
from .services.formula_service import FormulaService
from .services.pdf_service import PDFService
from .services.problem_service import ProblemService
from .services.quiz_service import QuizService
from .services.practice_service import PracticeService

from .utils.config import (
    COURSES_DIR,
    DATA_DIR,
    DISCORD_TOKEN,
)


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)


class MathdylBot(
    commands.Bot
):

    def __init__(self):

        intents = discord.Intents.default()

        super().__init__(
            command_prefix="!",
            intents=intents,
        )

        # ==========================================
        # SERVICES
        # ==========================================

        self.content_service = (
            ContentService(
                DATA_DIR
            )
        )

        self.course_service = (
            CourseService(
                self.content_service,
                COURSES_DIR,
            )
        )

        self.formula_service = (
            FormulaService(
                self.content_service
            )
        )

        self.problem_service = (
            ProblemService(
                self.content_service
            )
        )

        self.daily_service = (
            DailyService(
                self.content_service
            )
        )

        self.practice_service = (
            PracticeService(
                self.course_service
            )
        )

        self.quiz_service = (
            QuizService(
                self.course_service
            )
        )

        # ==========================================
        # PDF
        # ==========================================

        self.pdf_service = (
            PDFService()
        )

        # ==========================================
        # AI
        # ==========================================

        self.ai_service = (
            AIService()
        )

    async def setup_hook(self):

        extensions = [
            "src.cogs.general",
            "src.cogs.formulas",
            "src.cogs.daily",
            "src.cogs.problems",
            "src.cogs.courses",
            "src.cogs.quizzes",
            "src.cogs.launchers"
        ]

        for extension in extensions:

            try:

                await self.load_extension(
                    extension
                )

                logging.info(
                    "Loaded extension: %s",
                    extension,
                )

            except Exception:

                logging.exception(
                    "Failed to load extension: %s",
                    extension,
                )

        synced = (
            await self.tree.sync()
        )

        logging.info(
            "Synced %d slash commands.",
            len(synced),
        )

    async def on_ready(self):

        logging.info(
            "Logged in as %s",
            self.user,
        )

        logging.info(
            "Course directories discovered: %d",
            len(
                self.course_service.discover()
            ),
        )


async def main():

    bot = MathdylBot()

    async with bot:

        await bot.start(
            DISCORD_TOKEN
        )


if __name__ == "__main__":

    asyncio.run(
        main()
    )