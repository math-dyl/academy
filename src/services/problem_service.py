from __future__ import annotations

import random


class ProblemService:

    def __init__(
        self,
        content_service,
    ):

        self.content = content_service

    def all(self) -> list[dict]:

        data = self.content.load_general(
            "problems.json",
            [],
        )

        return self._as_list(data)

    def random(self) -> dict | None:

        problems = self.all()

        if not problems:
            return None

        return random.choice(problems)

    @staticmethod
    def _as_list(data):

        if isinstance(data, list):
            return data

        if isinstance(data, dict):

            problems = data.get(
                "problems",
                [],
            )

            if isinstance(
                problems,
                list,
            ):
                return problems

        return []