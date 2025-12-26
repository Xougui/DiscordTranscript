import unicodedata

import aiohttp
import emoji
from grapheme import graphemes

from DiscordTranscript.ext.cache import cache

cdn_fmt = (
    "https://cdn.jsdelivr.net/gh/jdecked/twemoji@latest/assets/72x72/{codepoint}.png"
)


@cache()
async def valid_src(src: str) -> bool:
    """Checks if a URL is valid.

    Args:
        src (str): The URL to check.

    Returns:
        bool: Whether the URL is valid.
    """
    try:
        async with aiohttp.ClientSession() as session, session.get(src) as resp:
            return resp.status == 200
    except aiohttp.ClientConnectorError:
        return False


def valid_category(char: str) -> bool:
    """Checks if a character is a valid emoji category.

    Args:
        char (str): The character to check.

    Returns:
        bool: Whether the character is a valid emoji category.
    """
    try:
        return unicodedata.category(char) == "So"
    except TypeError:
        return False


async def codepoint(codes: list) -> str:
    """Converts a list of codes to a string.

    Args:
        codes (list): The list of codes to convert.

    Returns:
        str: The converted string.
    """
    if "200d" not in codes:
        return "-".join([c for c in codes if c != "fe0f"])
    return "-".join(codes)


async def convert(char: str) -> str:
    """Converts a character to an emoji image.

    Args:
        char (str): The character to convert.

    Returns:
        str: The HTML for the emoji image.
    """
    if valid_category(char):
        name = unicodedata.name(char).title()
    else:
        if len(char) == 1:
            return char
        else:
            shortcode = emoji.demojize(char)
            name = (
                shortcode.replace(":", "")
                .replace("_", " ")
                .replace("selector", "")
                .title()
            )

    src = cdn_fmt.format(codepoint=await codepoint([f"{ord(c):x}" for c in char]))

    if await valid_src(src):
        return f'<img class="emoji emoji--small" src="{src}" alt="{char}" title="{name}" aria-label="Emoji: {name}">'
    else:
        return char


async def convert_emoji(string: str) -> str:
    """Converts a string of emojis to a string of emoji images.

    Args:
        string (str): The string to convert.

    Returns:
        str: The converted string.
    """
    x = []
    for ch in graphemes(string):
        x.append(await convert(ch))
    return "".join(x)
