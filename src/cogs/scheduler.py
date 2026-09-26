from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands, tasks


class SchedulerCog(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.base_path = (
            Path(__file__)
            .resolve()
            .parents[2]
        )

        self.schedule_path = (
            self.base_path
            / "data"
            / "config"
            / "schedule.json"
        )

        self.state_path = (
            self.base_path
            / "data"
            / "config"
            / "scheduler_state.json"
        )

        self.schedule = self.load_schedule()

        self.daily.start()

    def cog_unload(self):

        self.daily.cancel()

    # ==================================================
    # LOAD SCHEDULE
    # ==================================================

    def load_schedule(self):

        if not self.schedule_path.exists():

            print(
                "[Scheduler] schedule.json "
                "was not found."
            )

            return {}

        try:

            with self.schedule_path.open(
                "r",
                encoding="utf-8",
            ) as file:

                return json.load(file)

        except (
            json.JSONDecodeError,
            OSError,
        ) as error:

            print(
                f"[Scheduler] Failed to load "
                f"schedule.json: {error}"
            )

            return {}

    # ==================================================
    # LOAD STATE
    # ==================================================

    def load_state(self):

        if not self.state_path.exists():
            return {}

        try:

            with self.state_path.open(
                "r",
                encoding="utf-8",
            ) as file:

                return json.load(file)

        except (
            json.JSONDecodeError,
            OSError,
        ):

            return {}

    # ==================================================
    # SAVE STATE
    # ==================================================

    def save_state(
        self,
        state,
    ):

        self.state_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.state_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                state,
                file,
                indent=4,
            )

    # ==================================================
    # GET CHANNEL
    # ==================================================

    async def get_channel(
        self,
        channel_id,
    ):

        try:

            channel_id = int(channel_id)

        except (
            TypeError,
            ValueError,
        ):

            return None

        channel = self.bot.get_channel(
            channel_id
        )

        if channel is not None:
            return channel

        try:

            channel = await self.bot.fetch_channel(
                channel_id
            )

            return channel

        except (
            discord.NotFound,
            discord.Forbidden,
            discord.HTTPException,
        ):

            return None

    # ==================================================
    # CHECK IF ALREADY POSTED
    # ==================================================

    def already_posted(
        self,
        state,
        date_key,
        event_name,
    ):

        return (
            state
            .get(date_key, {})
            .get(event_name, False)
        )

    # ==================================================
    # MARK AS POSTED
    # ==================================================

    def mark_posted(
        self,
        state,
        date_key,
        event_name,
    ):

        if date_key not in state:

            state[date_key] = {}

        state[date_key][event_name] = True

        self.save_state(state)

    # ==================================================
    # DAILY SCHEDULER
    # ==================================================

    @tasks.loop(minutes=1)
    async def daily(self):

        timezone_name = (
            self.schedule
            .get(
                "timezone",
                "Asia/Manila",
            )
        )

        try:

            timezone = ZoneInfo(
                timezone_name
            )

        except Exception:

            timezone = ZoneInfo(
                "Asia/Manila"
            )

        now = datetime.now(timezone)

        current_time = now.strftime(
            "%H:%M"
        )

        date_key = now.strftime(
            "%Y-%m-%d"
        )

        daily_config = (
            self.schedule
            .get(
                "daily",
                {},
            )
        )

        state = self.load_state()

        # ==============================================
        # FORMULA
        # ==============================================

        formula_config = (
            daily_config
            .get(
                "formula",
                {},
            )
        )

        if (
            formula_config.get(
                "enabled",
                False,
            )
            and formula_config.get(
                "time"
            ) == current_time
            and not self.already_posted(
                state,
                date_key,
                "formula",
            )
        ):

            channel = await self.get_channel(
                formula_config.get(
                    "channel_id"
                )
            )

            if channel:

                daily_cog = self.bot.get_cog(
                    "DailyCog"
                )

                if daily_cog:

                    success = await (
                        daily_cog
                        .send_formula_of_the_day(
                            channel
                        )
                    )

                    if success:

                        self.mark_posted(
                            state,
                            date_key,
                            "formula",
                        )

                        print(
                            "[Scheduler] "
                            "Formula of the Day posted."
                        )

        # ==============================================
        # PROBLEM
        # ==============================================

        problem_config = (
            daily_config
            .get(
                "problem",
                {},
            )
        )

        if (
            problem_config.get(
                "enabled",
                False,
            )
            and problem_config.get(
                "time"
            ) == current_time
            and not self.already_posted(
                state,
                date_key,
                "problem",
            )
        ):

            channel = await self.get_channel(
                problem_config.get(
                    "channel_id"
                )
            )

            if channel:

                daily_cog = self.bot.get_cog(
                    "DailyCog"
                )

                if daily_cog:

                    success = await (
                        daily_cog
                        .send_problem_of_the_day(
                            channel
                        )
                    )

                    if success:

                        self.mark_posted(
                            state,
                            date_key,
                            "problem",
                        )

                        print(
                            "[Scheduler] "
                            "Problem of the Day posted."
                        )

        # ==============================================
        # TRIVIA
        # ==============================================

        trivia_config = (
            daily_config
            .get(
                "trivia",
                {},
            )
        )

        if (
            trivia_config.get(
                "enabled",
                False,
            )
            and trivia_config.get(
                "time"
            ) == current_time
            and not self.already_posted(
                state,
                date_key,
                "trivia",
            )
        ):

            channel = await self.get_channel(
                trivia_config.get(
                    "channel_id"
                )
            )

            if channel:

                daily_cog = self.bot.get_cog(
                    "DailyCog"
                )

                if daily_cog:

                    success = await (
                        daily_cog
                        .send_trivia(
                            channel
                        )
                    )

                    if success:

                        self.mark_posted(
                            state,
                            date_key,
                            "trivia",
                        )

                        print(
                            "[Scheduler] "
                            "Math Trivia posted."
                        )

    # ==================================================
    # BOT READY
    # ==================================================

    @daily.before_loop
    async def before_daily(self):

        await self.bot.wait_until_ready()

        self.schedule = (
            self.load_schedule()
        )


async def setup(bot):

    await bot.add_cog(
        SchedulerCog(bot)
    )