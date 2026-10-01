from __future__ import annotations

import logging
import traceback

import discord
from discord.ext import commands


logger = logging.getLogger(__name__)

LAUNCHER_MARKER = "MATHDYL_TOPIC_LAUNCHER"


class TopicLauncherView(discord.ui.View):

    def __init__(
        self,
        bot,
        course: str,
        topic: str,
    ):
        super().__init__(
            timeout=None
        )

        self.bot = bot
        self.course = course
        self.topic = topic

    # ==================================================
    # ==================================================
    # START LEARNING
    # ==================================================

    @discord.ui.button(
        label="Start Learning",
        style=discord.ButtonStyle.primary,
        emoji="📖",
        custom_id="mathdyl:start_learning",
    )
    async def start_learning(self, interaction: discord.Interaction, button: discord.ui.Button):
        lessons = self.bot.course_service.lessons(self.course, self.topic)
        if not lessons:
            await interaction.response.send_message("No lessons are available for this topic.", ephemeral=True)
            return
        try:
            await self.bot.database_service.upsert_user(
                user_id=interaction.user.id,
                username=interaction.user.name,
                display_name=interaction.user.display_name,
            )
            progress = await self.bot.database_service.get_course_progress(
                interaction.user.id, self.course, self.topic
            )
        except Exception:
            logger.exception("Could not load topic progress.")
            await interaction.response.send_message(
                "I couldn't load your saved progress right now. Please try again shortly.",
                ephemeral=True,
            )
            return

        if progress.get("completed"):
            view = CompletedTopicView(
                bot=self.bot, course=self.course, topic=self.topic,
                lessons=lessons, user_id=interaction.user.id,
            )
            embed = discord.Embed(
                title="✅ Topic Completed",
                description="You have completed this topic. Would you like to restart it?",
                color=0x16A34A,
            )
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            return

        raw_index = progress.get("lesson_index", 0)
        try:
            index = int(raw_index)
        except (TypeError, ValueError, OverflowError):
            index = 0
        # lessons.json is a flat list: lessons, examples, and concept checks
        # each occupy one displayable content index.
        index = max(0, min(index, len(lessons) - 1))
        if not progress.get("exists") or index != raw_index:
            try:
                await self.bot.database_service.save_course_progress(
                    interaction.user.id, self.course, self.topic, index
                )
            except Exception:
                logger.exception("Could not initialize or repair topic progress.")
                await interaction.response.send_message(
                    "I couldn't save your progress right now. Please try again shortly.",
                    ephemeral=True,
                )
                return

        await _start_lesson(
            interaction, self.bot, self.course, self.topic, lessons, index
        )


class CompletedTopicView(discord.ui.View):
    def __init__(self, bot, course, topic, lessons, user_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.course = course
        self.topic = topic
        self.lessons = lessons
        self.user_id = user_id

    async def _check_owner(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user_id:
            return True
        await interaction.response.send_message("This learning session belongs to another user.", ephemeral=True)
        return False

    @discord.ui.button(label="Restart Topic", style=discord.ButtonStyle.primary)
    async def restart(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_owner(interaction):
            return
        try:
            await self.bot.database_service.reset_course_progress(self.user_id, self.course, self.topic)
        except Exception:
            logger.exception("Could not restart completed topic.")
            await interaction.response.send_message(
                "I couldn't restart this topic right now. Please try again shortly.",
                ephemeral=True,
            )
            return
        await _start_lesson(
            interaction, self.bot, self.course, self.topic, self.lessons, 0,
            replace_message=True,
        )


async def _start_lesson(
    interaction, bot, course, topic, lessons, index: int, replace_message: bool = False
):
    """Persist the starting position before displaying the lesson view."""
    from .courses import LessonView

    try:
        await bot.database_service.save_course_progress(
            interaction.user.id, course, topic, index
        )
    except Exception:
        logger.exception("Could not save lesson start position.")
        await interaction.response.send_message(
            "I couldn't save your progress right now. Please try again shortly.",
            ephemeral=True,
        )
        return
    view = LessonView(
        bot=bot, course=course, topic=topic, lessons=lessons,
        user_id=interaction.user.id, start_index=index,
    )
    if replace_message:
        await interaction.response.edit_message(
            content=None,
            embed=view.make_embed(),
            view=view,
        )
    else:
        await interaction.response.send_message(
            embed=view.make_embed(), view=view, ephemeral=True
        )



# TOPIC LAUNCHER COG
# ======================================================

class TopicLauncherCog(
    commands.Cog
):

    def __init__(
        self,
        bot,
    ):
        self.bot = bot

        self.launchers_started = False

    # ==================================================
    # BOT READY
    # ==================================================

    @commands.Cog.listener()
    async def on_ready(self):

        if self.launchers_started:
            return

        self.launchers_started = True

        await self.launch_all_topics()

    # ==================================================
    # LAUNCH ALL TOPICS
    # ==================================================

    async def launch_all_topics(self):

        topics = (
            self.bot.course_service.discover()
        )

        print(
            f"Found {len(topics)} topic(s)."
        )

        for topic in topics:

            try:

                await self.launch_topic(
                    topic.course,
                    topic.topic,
                )

            except Exception:
                traceback.print_exc()

    # ==================================================
    # LAUNCH ONE TOPIC
    # ==================================================

    async def launch_topic(
        self,
        course: str,
        topic: str,
    ):

        channel_id = (
            self.bot.course_service.channel_id(
                course,
                topic,
            )
        )

        if not channel_id:

            print(
                f"[SKIP] "
                f"{course}/{topic}: "
                "No channel_id."
            )

            return

        channel = (
            self.bot.get_channel(
                channel_id
            )
        )

        if channel is None:

            try:

                channel = (
                    await self.bot.fetch_channel(
                        channel_id
                    )
                )

            except discord.NotFound:

                print(
                    f"[SKIP] "
                    f"{course}/{topic}: "
                    f"Channel {channel_id} not found."
                )

                return

            except discord.Forbidden:

                print(
                    f"[SKIP] "
                    f"{course}/{topic}: "
                    "Bot has no permission."
                )

                return

        if not isinstance(
            channel,
            discord.TextChannel,
        ):

            print(
                f"[SKIP] "
                f"{course}/{topic}: "
                "Channel is not a text channel."
            )

            return

        config = (
            self.bot.course_service.course_config(
                course,
                topic,
            )
        )

        title = config.get(
            "title",
            topic.replace(
                "-",
                " ",
            ).title(),
        )

        description = config.get(
            "description",
            "Continue your learning journey "
            "with Mathdyl Academy.",
        )

        embed = discord.Embed(
            title=f"📚 {title}",
            description=(
                f"{description}\n\n"
                "Choose an option below to begin."
            ),
            color=0x2563EB,
        )

        embed.set_footer(
            text=(
                f"Mathdyl Academy • "
                f"{course} / {topic}"
            )
        )

        # ==============================================
        # CHECK EXISTING LAUNCHER
        # ==============================================

        existing_message = (
            await self.find_launcher(
                channel
            )
        )

        view = TopicLauncherView(
            bot=self.bot,
            course=course,
            topic=topic,
        )

        if existing_message:

            try:

                await existing_message.edit(
                    embed=embed,
                    view=view,
                )

                print(
                    f"[UPDATED] "
                    f"{course}/{topic} "
                    f"→ #{channel.name}"
                )

            except discord.Forbidden:

                print(
                    f"[FORBIDDEN] "
                    f"Cannot edit launcher "
                    f"in #{channel.name}"
                )

            return

        # ==============================================
        # CREATE NEW LAUNCHER
        # ==============================================

        message = await channel.send(
            content=LAUNCHER_MARKER,
            embed=embed,
            view=view,
        )

        # Hide marker from normal users
        await message.edit(
            content=None
        )

        print(
            f"[CREATED] "
            f"{course}/{topic} "
            f"→ #{channel.name}"
        )

    # ==================================================
    # FIND EXISTING LAUNCHER
    # ==================================================

    async def find_launcher(
        self,
        channel: discord.TextChannel,
    ):

        try:

            async for message in channel.history(
                limit=100
            ):

                if (
                    message.author.id
                    != self.bot.user.id
                ):
                    continue

                if not message.embeds:
                    continue

                embed = message.embeds[0]

                footer = (
                    embed.footer.text
                    if embed.footer
                    else ""
                )

                if (
                    "Mathdyl Academy"
                    in footer
                ):

                    return message

        except discord.Forbidden:

            print(
                f"[FORBIDDEN] "
                f"Cannot read #{channel.name}"
            )

        return None


# ======================================================
# SETUP
# ======================================================

async def setup(bot):

    await bot.add_cog(
        TopicLauncherCog(bot)
    )