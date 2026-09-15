from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / os.getenv(
    "DATA_DIR",
    "data",
)

GENERAL_DIR = DATA_DIR / "general"

# IMPORTANT:
# Your course structure starts here:
#
# data/courses/<course>/<subject>/<topic>/
#
COURSES_DIR = DATA_DIR / "courses"


# --------------------------------------------------
# DISCORD
# --------------------------------------------------

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")

COMMAND_PREFIX = os.getenv(
    "COMMAND_PREFIX",
    "!",
)


# --------------------------------------------------
# EMBED
# --------------------------------------------------

EMBED_COLOR = int(
    os.getenv(
        "EMBED_COLOR",
        "2563EB",
    ),
    16,
)


# --------------------------------------------------
# AI
# --------------------------------------------------

AI_ENABLED = (
    os.getenv(
        "AI_ENABLED",
        "false",
    ).lower()
    == "true"
)

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:7b-instruct",
)


if not DISCORD_TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN is missing. "
        "Add it to your .env file."
    )