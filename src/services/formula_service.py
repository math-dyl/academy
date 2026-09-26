from __future__ import annotations


class FormulaService:

    def __init__(
        self,
        content_service,
    ):
        self.content = content_service

    def get_cheatsheet(
        self,
        category: str,
    ) -> dict | None:

        category = category.strip().lower()

        data = self.content.load_formula(
            f"{category}.json",
            None,
        )

        if not isinstance(data, dict):
            return None

        return data