
from __future__ import annotations

import random


class DailyService:

    def __init__(
        self,
        content_service,
    ):

        self.content = content_service

    # ==================================================
    # FORMULA OF THE DAY
    # ==================================================

    def formula_of_the_day(self):

        data = self.content.load_daily(
            "formulas.json",
            [],
        )

        return self._random_item(
            data
        )

    # ==================================================
    # PROBLEM OF THE DAY
    # ==================================================

    def problem_of_the_day(self):

        data = self.content.load_daily(
            "problems.json",
            [],
        )

        return self._random_item(
            data
        )

    # ==================================================
    # SOLUTION OF THE DAY
    # ==================================================

    def solution_of_the_day(self):

        data = self.content.load_daily(
            "solutions.json",
            [],
        )

        return self._random_item(
            data
        )

    # ==================================================
    # TRIVIA OF THE DAY
    # ==================================================

    def trivia_of_the_day(self):

        data = self.content.load_daily(
            "trivia.json",
            [],
        )

        return self._random_item(
            data
        )

    # ==================================================
    # RANDOM ITEM
    # ==================================================

    @staticmethod
    def _random_item(data):

        if isinstance(
            data,
            list,
        ):

            if not data:
                return None

            return random.choice(
                data
            )

        if isinstance(
            data,
            dict,
        ):

            for key in (
                "items",
                "formulas",
                "problems",
                "solutions",
                "trivia",
            ):

                values = data.get(
                    key
                )

                if isinstance(
                    values,
                    list,
                ) and values:

                    return random.choice(
                        values
                    )

            return data

        return None

