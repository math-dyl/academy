from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ContentService:

    def __init__(
        self,
        data_dir: Path,
    ):
        self.data_dir = Path(data_dir)

    # --------------------------------------------------
    # JSON
    # --------------------------------------------------

    def load_json(
        self,
        path: Path,
        default: Any = None,
    ) -> Any:

        if not path.exists():

            return (
                {}
                if default is None
                else default
            )

        try:

            return json.loads(
                path.read_text(
                    encoding="utf-8",
                )
            )

        except (
            json.JSONDecodeError,
            OSError,
        ):

            return (
                {}
                if default is None
                else default
            )

    def save_json(
        self,
        path: Path,
        data: Any,
    ) -> None:

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    # --------------------------------------------------
    # GENERAL
    # --------------------------------------------------

    def load_general(
        self,
        filename: str,
        default=None,
    ):

        path = (
            self.data_dir
            / "general"
            / filename
        )

        return self.load_json(
            path,
            default,
        )

    # --------------------------------------------------
    # DIRECTORY
    # --------------------------------------------------

    def list_json_files(
        self,
        directory: Path,
    ) -> list[Path]:

        if not directory.exists():
            return []

        return sorted(
            path
            for path in directory.glob("*.json")
            if path.is_file()
        )