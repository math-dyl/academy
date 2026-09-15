from __future__ import annotations

import re
from typing import Any


def slugify(value: str) -> str:
    """
    Convert text into a filesystem/command-friendly slug.

    Example:
        "Real Numbers" -> "real-numbers"
    """

    value = value.strip().lower()

    value = re.sub(
        r"[^a-z0-9]+",
        "-",
        value,
    )

    return value.strip("-")


def truncate(
    text: Any,
    limit: int = 1000,
) -> str:

    text = str(text)

    if len(text) <= limit:
        return text

    return text[: limit - 3] + "..."


def chunk_text(
    text: str,
    size: int = 3500,
) -> list[str]:

    text = str(text)

    if not text:
        return [""]

    return [
        text[index:index + size]
        for index in range(
            0,
            len(text),
            size,
        )
    ]


def first_value(
    data: dict,
    *keys: str,
    default: Any = "",
):
    """
    Return the first existing value from a dictionary.
    """

    for key in keys:

        if key in data:
            value = data[key]

            if value is not None:
                return value

    return default


def as_list(data: Any) -> list:

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        possible_keys = [
            "items",
            "data",
            "lessons",
            "examples",
            "practice",
            "questions",
            "quizzes",
            "formulas",
            "problems",
        ]

        for key in possible_keys:

            value = data.get(key)

            if isinstance(value, list):
                return value

    return []