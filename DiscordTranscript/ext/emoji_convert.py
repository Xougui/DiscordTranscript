import asyncio
import unicodedata

import aiohttp
import emoji
from grapheme import graphemes

from DiscordTranscript.ext.cache import cache

cdn_fmt = (
    "https://cdn.jsdelivr.net/gh/jdecked/twemoji@latest/assets/72x72/{codepoint}.png"
)


@cache()
async def valid_src(src: str, session: aiohttp.ClientSession | None = None) -> bool:
    """Checks if a URL is valid.

    Args:
        src (str): The URL to check.
        session (Optional[aiohttp.ClientSession]): Shared HTTP session.

    Returns:
        bool: Whether the URL is valid.
    """
    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True

    try:
        async with session.get(src) as resp:
            return resp.status == 200
    except (aiohttp.ClientConnectorError, aiohttp.ClientError):
        return False
    finally:
        if close_session:
            await session.close()


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


async def convert(char: str, session: aiohttp.ClientSession | None = None) -> str:
    """Converts a character to an emoji image.

    Args:
        char (str): The character to convert.
        session (Optional[aiohttp.ClientSession]): Shared HTTP session.

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

    if await valid_src(src, session=session):
        return f'<img class="emoji emoji--small" src="{src}" alt="{char}" title="{name}" aria-label="Emoji: {name}">'
    else:
        return char


async def convert_emoji(
    string: str, session: aiohttp.ClientSession | None = None
) -> str:
    """Converts a string of emojis to a string of emoji images concurrently.

    Args:
        string (str): The string to convert.
        session (Optional[aiohttp.ClientSession]): Shared HTTP session.

    Returns:
        str: The converted string.
    """
    grapheme_list = list(graphemes(string))
    if not grapheme_list:
        return ""

    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True

    try:
        results = await asyncio.gather(
            *(convert(ch, session=session) for ch in grapheme_list)
        )
        return "".join(results)
    finally:
        if close_session:
            await session.close()
