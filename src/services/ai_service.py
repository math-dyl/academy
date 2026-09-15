from __future__ import annotations

import httpx

from ..utils.config import (
    AI_ENABLED,
    OLLAMA_MODEL,
    OLLAMA_URL,
)


class AIService:

    def __init__(self):

        self.enabled = AI_ENABLED

        self.url = (
            OLLAMA_URL.rstrip("/")
        )

        self.model = OLLAMA_MODEL

    async def ask(
        self,
        prompt: str,
    ) -> str:

        if not self.enabled:

            return (
                "AI Assistant is currently disabled.\n\n"
                "Set `AI_ENABLED=true` in `.env` "
                "to enable it."
            )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        try:

            async with httpx.AsyncClient(
                timeout=120
            ) as client:

                response = await client.post(
                    f"{self.url}/api/generate",
                    json=payload,
                )

                response.raise_for_status()

                data = response.json()

                return data.get(
                    "response",
                    "No response returned.",
                )

        except Exception as error:

            return (
                "I could not connect to the AI "
                f"service.\n\n`{error}`"
            )