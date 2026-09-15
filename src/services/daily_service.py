from __future__ import annotations

import random


class DailyService:

    def __init__(
        self,
        content_service,
    ):

        self.content = content_service

    def formula_of_the_day(self):

        data = self.content.load_general(
            "formula_of_the_day.json",
            [],
        )

        return self._random_item(
            data
        )

    def problem_of_the_day(self):

        data = self.content.load_general(
            "problem_of_the_day.json",
            [],
        )

        return self._random_item(
            data
        )

    @staticmethod
    def _random_item(data):

        if isinstance(
            data,
            list,
        ):

            if not data:
                return None

            return random.choice(data)

        if isinstance(
            data,
            dict,
        ):

            for key in (
                "items",
                "formulas",
                "problems",
            ):

                values = data.get(key)

                if isinstance(
                    values,
                    list,
                ) and values:

                    return random.choice(
                        values
                    )

            return data

        return None