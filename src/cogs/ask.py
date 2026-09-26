
from __future__ import annotations

import asyncio
import logging

import discord

from discord import app_commands
from discord.ext import commands


logger = logging.getLogger(__name__)


# ==================================================
# ASK COG
# ==================================================

class AskCog(commands.Cog):

    def __init__(
        self,
        bot: commands.Bot,
    ):

        self.bot = bot

    # ==================================================
    # /ask
    # ==================================================

    @app_commands.command(
        name="ask",
        description="Ask the Mathdyl AI Math Assistant.",
    )
    @app_commands.describe(
        question="Ask a mathematics question."
    )
    async def ask(
        self,
        interaction: discord.Interaction,
        question: str,
    ):

        ai_service = self.bot.ai_service

        # ==========================================
        # AI DISABLED
        # ==========================================

        if not ai_service.is_enabled():

            await interaction.response.send_message(
                "The Mathdyl AI Assistant is currently disabled.",
                ephemeral=True,
            )

            return

        # ==========================================
        # DEFER
        # ==========================================

        await interaction.response.defer(
            ephemeral=True
        )

        try:

            # ======================================
            # QUESTION EMBED
            # ======================================

            question_embed = discord.Embed(
                title="❓ Student Question",
                description=question[:4000],
                color=discord.Color.blurple(),
            )

            question_embed.set_footer(
                text="Mathdyl AI"
            )

            # ======================================
            # SEND QUESTION EMBED
            # ======================================

            await interaction.followup.send(
                embed=question_embed,
                ephemeral=True,
            )

            # ======================================
            # AI RESPONSE EMBED
            # ======================================

            response_embed = discord.Embed(
                title="🤖 Mathdyl AI",
                description="Thinking...",
                color=discord.Color.blue(),
            )

            response_embed.set_footer(
                text=f"Generating with {ai_service.model}"
            )

            # ======================================
            # SEND AI RESPONSE EMBED
            #
            # wait=True returns the actual message
            # so we can edit it while streaming.
            # ======================================

            response_message = (
                await interaction.followup.send(
                    embed=response_embed,
                    ephemeral=True,
                    wait=True,
                )
            )

            # ======================================
            # STREAM RESPONSE
            # ======================================

            full_response = ""

            last_update = 0.0

            async for chunk in ai_service.ask_stream(
                question
            ):

                # ----------------------------------
                # ADD NEW CHUNK
                # ----------------------------------

                full_response += chunk

                current_time = (
                    asyncio.get_running_loop().time()
                )

                # ----------------------------------
                # UPDATE DISCORD EVERY ~0.8 SEC
                # ----------------------------------

                if (
                    current_time - last_update
                    < 0.8
                ):
                    continue

                last_update = current_time

                display = (
                    full_response.strip()
                    or "Thinking..."
                )

                # ----------------------------------
                # DISCORD EMBED DESCRIPTION LIMIT
                # ----------------------------------

                if len(display) > 4000:

                    display = (
                        display[:3990]
                        + "\n..."
                    )

                response_embed.description = (
                    display
                )

                # ----------------------------------
                # UPDATE AI MESSAGE
                # ----------------------------------

                await response_message.edit(
                    embed=response_embed
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
            # FINAL LENGTH PROTECTION
            # ======================================

            if len(final_response) > 4000:

                final_response = (
                    final_response[:3990]
                    + "\n..."
                )

            response_embed.description = (
                final_response
            )

            # ======================================
            # AI MODE FOOTER
            # ======================================

            if ai_service.is_local():

                response_embed.set_footer(
                    text=(
                        f"Local AI • "
                        f"{ai_service.model}"
                    )
                )

            else:

                response_embed.set_footer(
                    text=(
                        f"AI API • "
                        f"{ai_service.model}"
                    )
                )

            # ======================================
            # FINAL MESSAGE UPDATE
            # ======================================

            await response_message.edit(
                embed=response_embed
            )

        # ==========================================
        # ERROR HANDLING
        # ==========================================

        except Exception as e:

            logger.exception(
                "AI request failed"
            )

            error_embed = discord.Embed(
                title="❌ AI Error",
                description=(
                    "I couldn't connect to the AI service.\n\n"
                    f"```text\n"
                    f"{str(e)[:1500]}"
                    f"\n```"
                ),
                color=discord.Color.red(),
            )

            try:

                await interaction.edit_original_response(
                    embed=error_embed
                )

            except Exception:

                await interaction.followup.send(
                    embed=error_embed,
                    ephemeral=True,
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

