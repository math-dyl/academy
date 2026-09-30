
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import discord

from discord import app_commands
from discord.ext import commands

from ..utils.embeds import make_embed


logger = logging.getLogger(__name__)


# ==================================================
# CONFIGURATION
# ==================================================

DAILY_ASK_LIMIT = 3

TIMEZONE = ZoneInfo(
    "Asia/Manila"
)


# ==================================================
# ASK COG
# ==================================================

class AskCog(
    commands.Cog
):

    def __init__(
        self,
        bot: commands.Bot,
    ):

        self.bot = bot

        # ==========================================
        # USER DAILY USAGE
        #
        # {
        #     user_id: {
        #         "date": "2026-09-28",
        #         "count": 2
        #     }
        # }
        # ==========================================

        self.ask_usage: dict[
            int,
            dict
        ] = {}

    # ==================================================
    # DAILY LIMIT
    # ==================================================

    def get_daily_usage(
        self,
        user_id: int,
    ) -> int:

        today = datetime.now(
            TIMEZONE
        ).date().isoformat()

        user_data = self.ask_usage.get(
            user_id
        )

        # ==========================================
        # FIRST REQUEST
        # ==========================================

        if user_data is None:

            self.ask_usage[user_id] = {
                "date": today,
                "count": 0,
            }

            return 0

        # ==========================================
        # NEW DAY
        # ==========================================

        if user_data["date"] != today:

            self.ask_usage[user_id] = {
                "date": today,
                "count": 0,
            }

            return 0

        return user_data["count"]

    # ==================================================
    # INCREMENT DAILY USAGE
    # ==================================================

    def increment_daily_usage(
        self,
        user_id: int,
    ):

        today = datetime.now(
            TIMEZONE
        ).date().isoformat()

        self.ask_usage[user_id] = {
            "date": today,
            "count": (
                self.get_daily_usage(
                    user_id
                ) + 1
            ),
        }

    # ==================================================
    # FOOTER
    # ==================================================

    def get_ai_footer(
        self,
        ai_service,
        remaining: int,
    ) -> str:

        if ai_service.is_local():

            return (
                f"AI-Powered Solution • "
                f"{remaining} remaining today"
            )

        return (
            f"AI-Powered Solution • "
            f"{remaining} remaining today"
        )

    # ==================================================
    # /ask
    # ==================================================

    @app_commands.command(
        name="ask",
        description=(
            "Ask the Mathdyl AI Math Assistant."
        ),
    )
    @app_commands.describe(
        question=(
            "Ask a mathematics question."
        )
    )
    async def ask(
        self,
        interaction: discord.Interaction,
        question: str,
    ):

        user_id = interaction.user.id

        # ==========================================
        # CHECK DAILY LIMIT
        # ==========================================

        current_usage = (
            self.get_daily_usage(
                user_id
            )
        )

        if current_usage >= DAILY_ASK_LIMIT:

            await interaction.response.send_message(
                (
                    "⚠️ **Daily AI limit reached.**\n\n"
                    f"You have used all "
                    f"**{DAILY_ASK_LIMIT} AI questions** "
                    "for today.\n"
                    "Your limit will reset tomorrow."
                ),
                ephemeral=True,
            )

            return

        # ==========================================
        # AI SERVICE
        # ==========================================

        ai_service = self.bot.ai_service

        # ==========================================
        # AI DISABLED
        # ==========================================

        if not ai_service.is_enabled():

            await interaction.response.send_message(
                (
                    "The Mathdyl AI Assistant "
                    "is currently disabled."
                ),
                ephemeral=True,
            )

            return

        # ==========================================
        # COUNT REQUEST
        # ==========================================

        self.increment_daily_usage(
            user_id
        )

        remaining = (
            DAILY_ASK_LIMIT
            - self.get_daily_usage(
                user_id
            )
        )

        # ==========================================
        # DEFER
        # ==========================================

        await interaction.response.defer()

        response_message = None

        try:

            # ======================================
            # QUESTION EMBED
            # ======================================

            question_embed = make_embed(
                title="❓ Student Question",
                description=question,
            )

            question_embed.set_footer(
                text=(
                    f"Mathdyl AI • "
                    f"{remaining} questions "
                    f"remaining today"
                )
            )

            await interaction.followup.send(
                embed=question_embed,
            )

            # ======================================
            # INITIAL RESPONSE
            # ======================================

            response_message = (
                await interaction.followup.send(
                    content="Thinking...",
                    wait=True,
                )
            )

            # ======================================
            # STREAM RESPONSE
            # ======================================

            full_response = ""

            last_update = 0.0

            async for chunk in (
                ai_service.ask_stream(
                    question
                )
            ):

                full_response += chunk

                current_time = (
                    asyncio
                    .get_running_loop()
                    .time()
                )

                # ----------------------------------
                # Avoid editing too frequently
                # ----------------------------------

                if (
                    current_time
                    - last_update
                    < 0.8
                ):

                    continue

                last_update = current_time

                display = (
                    full_response.strip()
                    or "Thinking..."
                )

                # ----------------------------------
                # Protect Discord message limit
                # ----------------------------------

                if len(display) > 2000:

                    display = (
                        display[:1990]
                        + "\n..."
                    )

                await response_message.edit(
                    content=display,
                )

            # ======================================
            # FINAL RESPONSE
            # ======================================

            final_response = (
                full_response.strip()
            )

            if not final_response:

                final_response = (
                    "I couldn't generate a response."
                )

            # ======================================
            # PARSE RESPONSE
            # ======================================

            blocks = (
                ai_service
                .parse_response(
                    final_response
                )
            )

            # ======================================
            # FOOTER
            # ======================================

            footer_text = (
                self.get_ai_footer(
                    ai_service,
                    remaining,
                )
            )

            # ======================================
            # RENDER COMPLETE RESPONSE
            # ======================================

            images = (
                ai_service
                .equation_service
                .render_response(
                    blocks
                )
            )

            # ======================================
            # NO EQUATION
            # ======================================

            if images is None:

                await response_message.edit(
                    content=final_response,
                    embeds=[],
                    attachments=[],
                )

            # ======================================
            # HAS EQUATION
            # ======================================

            else:

                files = []
                embeds = []

                for index, image in enumerate(
                    images,
                    start=1,
                ):

                    filename = (
                        f"mathdyl_response_{index}.png"
                    )

                    files.append(
                        discord.File(
                            image,
                            filename=filename,
                        )
                    )

                    page_embed = discord.Embed(
                        color=discord.Color.blue(),
                    )

                    page_embed.set_image(
                        url=(
                            f"attachment://"
                            f"{filename}"
                        )
                    )

                    page_embed.set_footer(
                        text=(
                            f"{footer_text} • "
                            f"Page {index}/{len(images)}"
                        )
                    )

                    embeds.append(
                        page_embed
                    )

                await response_message.edit(
                    content=None,
                    embeds=embeds,
                    attachments=files,
                )

        # ==========================================
        # ERROR HANDLING
        # ==========================================

        except Exception as e:

            logger.exception(
                "AI request failed"
            )

            error_embed = make_embed(
                title="❌ AI Error",
                description=(
                    "I couldn't connect to "
                    "the AI service.\n\n"
                    f"```text\n"
                    f"{str(e)[:1500]}"
                    f"\n```"
                ),
                color=discord.Color.red().value,
            )

            try:

                if response_message is not None:

                    await response_message.edit(
                        embed=error_embed,
                        attachments=[],
                    )

                else:

                    await interaction.followup.send(
                        embed=error_embed,
                        ephemeral=True,
                    )

            except Exception:

                logger.exception(
                    "Failed to send AI error"
                )


# ==================================================
# SETUP
# ==================================================

async def setup(
    bot: commands.Bot,
):

    await bot.add_cog(
        AskCog(bot)
    )
