from __future__ import annotations

import discord

from .config import EMBED_COLOR
from .helpers import truncate


def make_embed(
    title: str,
    description: str = "",
    color: int = EMBED_COLOR,
) -> discord.Embed:

    return discord.Embed(
        title=truncate(
            title,
            256,
        ),
        description=truncate(
            description,
            4096,
        ),
        color=color,
    )


def add_fields(
    embed: discord.Embed,
    fields: list[tuple[str, str, bool]],
):

    for name, value, inline in fields:

        embed.add_field(
            name=truncate(
                name,
                256,
            ),
            value=truncate(
                value,
                1024,
            ),
            inline=inline,
        )

    return embed