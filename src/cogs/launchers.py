from __future__ import annotations

import traceback

import discord
from discord.ext import commands


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
    # START LEARNING
    # ==================================================

    @discord.ui.button(
        label="Start Learning",
        style=discord.ButtonStyle.primary,
        emoji="📖", 
        custom_id="mathdyl:start_learning",
    )
    async def start_learning(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        lessons = (
            self.bot.course_service.lessons(
                self.course,
                self.topic,
            )
        )

        if not lessons:
            await interaction.response.send_message(
                "No lessons are available for this topic.",
                ephemeral=True,
            )
            return

        from .courses import LessonView

        view = LessonView(
            bot=self.bot,
            course=self.course,
            topic=self.topic,
            lessons=lessons,
        )

        await interaction.response.send_message(
            embed=view.make_embed(),
            view=view,
            ephemeral=True,
        )

    

# ======================================================
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