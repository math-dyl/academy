from __future__ import annotations

import random


class FormulaService:

    def __init__(
        self,
        content_service,
    ):

        self.content = content_service

    def all(self) -> list[dict]:

        data = self.content.load_general(
            "formulas.json",
            [],
        )

        return self._as_list(data)

    def random(self) -> dict | None:

        items = self.all()

        if not items:
            return None

        return random.choice(items)

    @staticmethod
    def _as_list(data):

        if isinstance(data, list):
            return data

        if isinstance(data, dict):

            formulas = data.get(
                "formulas",
                [],
            )

            if isinstance(
                formulas,
                list,
            ):
                return formulas

        return []