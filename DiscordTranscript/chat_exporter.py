import datetime
import io
import os
from typing import List, Optional, TYPE_CHECKING

from DiscordTranscript.construct.transcript import Transcript
from DiscordTranscript.ext.discord_import import discord
from DiscordTranscript.construct.attachment_handler import AttachmentHandler, AttachmentToDataURIHandler, AttachmentToDiscordChannelHandler

if TYPE_CHECKING:
    import discord as discord_typings


async def quick_export(
    channel: "discord_typings.TextChannel",
    guild: Optional["discord_typings.Guild"] = None,
    bot: Optional["discord_typings.Client"] = None,
):
    """Creates a quick export of a Discord channel.

    This function will produce the transcript and post it back into the channel.

    Args:
        channel (discord.TextChannel): The Discord channel to export.
        guild (Optional[discord.Guild]): The guild the channel belongs to. Defaults to None.
        bot (Optional[discord.Client]): The bot instance. Defaults to None.

    Returns:
        discord.Message: The message containing the transcript.
    """

    if guild:
        channel.guild = guild

    transcript = (
        await Transcript(
            channel=channel,
            limit=None,
            messages=None,
            pytz_timezone="UTC",
            military_time=True,
            fancy_times=True,
            before=None,
            after=None,
            bot=bot,
            attachment_handler=None
            ).export()
        ).html

    if not transcript:
        return

    transcript_embed = discord.Embed(
        description=f"**Transcript Name:** transcript-{channel.name}\n\n",
        colour=discord.Colour.blurple()
    )

    transcript_file = discord.File(io.BytesIO(transcript.encode()), filename=f"transcript-{channel.name}.html")
    return await channel.send(embed=transcript_embed, file=transcript_file)


async def export(
    channel: "discord_typings.TextChannel",
    limit: Optional[int] = None,
    tz_info="UTC",
    guild: Optional["discord_typings.Guild"] = None,
    bot: Optional["discord_typings.Client"] = None,
    military_time: Optional[bool] = True,
    fancy_times: Optional[bool] = True,
    before: Optional[datetime.datetime] = None,
    after: Optional[datetime.datetime] = None,
    attachment_handler: Optional[AttachmentHandler] = None,
    tenor_api_key: Optional[str] = None,
):
    """Creates a customized transcript of a Discord channel.

    This function will return the transcript which you can then turn into a file.

    Args:
        channel (discord.TextChannel): The channel to export.
        limit (Optional[int]): The number of messages to fetch. Defaults to None (all messages).
        tz_info (str): The timezone to use for timestamps. Defaults to "UTC".
        guild (Optional[discord.Guild]): The guild the channel belongs to. Defaults to None.
        bot (Optional[discord.Client]): The bot instance. Defaults to None.
        military_time (bool): Whether to use military time. Defaults to True.
        fancy_times (bool): Whether to use fancy times. Defaults to True.
        before (Optional[datetime.datetime]): The date to fetch messages before. Defaults to None.
        after (Optional[datetime.datetime]): The date to fetch messages after. Defaults to None.
        attachment_handler (Optional[AttachmentHandler]): The attachment handler to use. Defaults to None.
        tenor_api_key (Optional[str]): The Tenor API key to use for fetching GIFs. Defaults to None.

    Returns:
        str: The transcript HTML.
    """
    if guild:
        channel.guild = guild

    tenor_api_key = tenor_api_key or os.getenv("TENOR_API_KEY")

    return (
        await Transcript(
            channel=channel,
            limit=limit,
            messages=None,
            pytz_timezone=tz_info,
            military_time=military_time,
            fancy_times=fancy_times,
            before=before,
            after=after,
            bot=bot,
            attachment_handler=attachment_handler,
            tenor_api_key=tenor_api_key,
        ).export()
    ).html


async def raw_export(
    channel: "discord_typings.TextChannel",
    messages: List["discord_typings.Message"],
    tz_info="UTC",
    guild: Optional["discord_typings.Guild"] = None,
    bot: Optional["discord_typings.Client"] = None,
    military_time: Optional[bool] = False,
    fancy_times: Optional[bool] = True,
    attachment_handler: Optional[AttachmentHandler] = None,
    tenor_api_key: Optional[str] = None,
):
    """Creates a customized transcript with your own captured Discord messages.

    This function will return the transcript which you can then turn into a file.

    Args:
        channel (discord.TextChannel): The channel to export.
        messages (List[discord.Message]): The messages to export.
        tz_info (str): The timezone to use for timestamps. Defaults to "UTC".
        guild (Optional[discord.Guild]): The guild the channel belongs to. Defaults to None.
        bot (Optional[discord.Client]): The bot instance. Defaults to None.
        military_time (bool): Whether to use military time. Defaults to False.
        fancy_times (bool): Whether to use fancy times. Defaults to True.
        attachment_handler (Optional[AttachmentHandler]): The attachment handler to use. Defaults to None.
        tenor_api_key (Optional[str]): The Tenor API key to use for fetching GIFs. Defaults to None.

    Returns:
        str: The transcript HTML.
    """
    if guild:
        channel.guild = guild

    tenor_api_key = tenor_api_key or os.getenv("TENOR_API_KEY")

    return (
        await Transcript(
            channel=channel,
            limit=None,
            messages=messages,
            pytz_timezone=tz_info,
            military_time=military_time,
            fancy_times=fancy_times,
            before=None,
            after=None,
            bot=bot,
            attachment_handler=attachment_handler,
            tenor_api_key=tenor_api_key
        ).export()
    ).html