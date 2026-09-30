from __future__ import annotations

import os
from pathlib import Path
from typing import AsyncGenerator

from dotenv import load_dotenv
from openai import AsyncOpenAI

from .equation_service import EquationService


# ==================================================
# ENVIRONMENT
# ==================================================

load_dotenv()


# ==================================================
# PATHS
# ==================================================

BASE_PATH = Path(__file__).resolve().parents[2]

PROMPT_PATH = (
    BASE_PATH
    / "src"
    / "prompts"
    / "ask.txt"
)


# ==================================================
# AI SERVICE
# ==================================================

class AIService:

    def __init__(self):

        # ==========================================
        # EQUATION SERVICE
        # ==========================================

        self.equation_service = (
            EquationService()
        )

        # ==========================================
        # API CONFIGURATION
        # ==========================================

        self.api_key = os.getenv(
            "AI_API_KEY",
            "",
        ).strip()

        # ==========================================
        # LOCAL OLLAMA
        # ==========================================

        if self.api_key.lower() == "false":

            self.enabled = True
            self.local_mode = True

            self.base_url = os.getenv(
                "AI_BASE_URL",
                "http://localhost:11434/v1",
            )

            self.model = os.getenv(
                "AI_MODEL",
                "qwen2.5:7b",
            )

            self.client_api_key = "ollama"

        # ==========================================
        # API MODE
        # ==========================================

        elif self.api_key:

            self.enabled = True
            self.local_mode = False

            self.base_url = os.getenv(
                "AI_BASE_URL",
                "https://api.openai.com/v1",
            )

            self.model = os.getenv(
                "AI_MODEL",
                "gpt-4o-mini",
            )

            self.client_api_key = (
                self.api_key
            )

        # ==========================================
        # DISABLED
        # ==========================================

        else:

            self.enabled = False
            self.local_mode = False

            self.base_url = ""
            self.model = ""
            self.client_api_key = ""

        # ==========================================
        # STREAMING
        # ==========================================

        self.streaming = (
            os.getenv(
                "AI_STREAMING",
                "true",
            ).lower()
            == "true"
        )

        # ==========================================
        # SYSTEM PROMPT
        # ==========================================

        if PROMPT_PATH.exists():

            self.system_prompt = (
                PROMPT_PATH.read_text(
                    encoding="utf-8"
                )
            )

        else:

            self.system_prompt = ""

        # ==========================================
        # CLIENT
        # ==========================================

        self.client = None

        if self.enabled:

            self.client = AsyncOpenAI(
                api_key=self.client_api_key,
                base_url=self.base_url,
            )

    # ==================================================
    # STATUS
    # ==================================================

    def is_enabled(
        self,
    ) -> bool:

        return self.enabled

    # ==================================================
    # LOCAL MODE
    # ==================================================

    def is_local(
        self,
    ) -> bool:

        return (
            self.enabled
            and self.local_mode
        )

    # ==================================================
    # PARSE AI RESPONSE
    # ==================================================

    def parse_response(
        self,
        content: str,
    ):

        return (
            self
            .equation_service
            .parse(
                content
            )
        )

    # ==================================================
    # NORMAL AI REQUEST
    # ==================================================

    async def ask(
        self,
        question: str,
    ) -> list[tuple[str, str]]:

        if not self.enabled:

            raise RuntimeError(
                "AI Assistant is disabled."
            )

        response = (
            await self.client
            .chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            self.system_prompt
                        ),
                    },
                    {
                        "role": "user",
                        "content": question,
                    },
                ],
                temperature=0.2,
                stream=False,
            )
        )

        content = (
            response
            .choices[0]
            .message
            .content
        ) or ""

        return self.parse_response(
            content
        )

    # ==================================================
    # STREAMING AI REQUEST
    # ==================================================

    async def ask_stream(
        self,
        question: str,
    ) -> AsyncGenerator[str, None]:

        if not self.enabled:

            raise RuntimeError(
                "AI Assistant is disabled."
            )

        stream = (
            await self.client
            .chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            self.system_prompt
                        ),
                    },
                    {
                        "role": "user",
                        "content": question,
                    },
                ],
                temperature=0.2,
                stream=True,
            )
        )

        async for chunk in stream:

            if not chunk.choices:

                continue

            delta = (
                chunk
                .choices[0]
                .delta
            )

            if delta.content:

                yield delta.content