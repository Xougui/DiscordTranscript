import datetime
import html
import re
import traceback
from typing import Optional

import pytz

from DiscordTranscript.construct.assets.component import Component
from DiscordTranscript.construct.attachment_handler import AttachmentHandler
from DiscordTranscript.construct.message import gather_messages
from DiscordTranscript.ext.cache import clear_cache
from DiscordTranscript.ext.discord_import import discord
from DiscordTranscript.ext.discord_utils import DiscordUtils
from DiscordTranscript.ext.html_generator import (
    PARSE_MODE_HTML_SAFE,
    PARSE_MODE_NONE,
    channel_subject,
    channel_topic,
    fancy_time,
    fill_out,
    meta_data_temp,
    total,
)


class TranscriptDAO:
    """A class to create a transcript of a Discord channel.

    Attributes:
        html (str): The HTML of the transcript.
        channel (discord.TextChannel): The channel to create a transcript of.
        limit (Optional[int]): The maximum number of messages to fetch.
        messages (Optional[List[discord.Message]]): A list of messages to use instead of fetching them.
        pytz_timezone (str): The timezone to use for the transcript.
        military_time (bool): Whether to use military time.
        fancy_times (bool): Whether to use fancy times.
        before (Optional[datetime.datetime]): The date to fetch messages before.
        after (Optional[datetime.datetime]): The date to fetch messages after.
        attachment_handler (Optional[AttachmentHandler]): The attachment handler to use.
        tenor_api_key (Optional[str]): The Tenor API key to use.
        bot (Optional[discord.Client]): The bot to use for fetching members.
    """

    html: str

    def __init__(
        self,
        channel: discord.TextChannel,
        limit: int | None,
        messages: list[discord.Message] | None,
        pytz_timezone,
        military_time: bool,
        fancy_times: bool,
        before: datetime.datetime | None,
        after: datetime.datetime | None,
        bot: Optional["discord.Client"],
        attachment_handler: AttachmentHandler | None,
        tenor_api_key: str | None = None,
    ) -> None:
        """Initializes the TranscriptDAO.

        Args:
            channel (discord.TextChannel): The channel to create a transcript of.
            limit (Optional[int]): The maximum number of messages to fetch.
            messages (Optional[List[discord.Message]]): A list of messages to use instead of fetching them.
            pytz_timezone (str): The timezone to use for the transcript.
            military_time (bool): Whether to use military time.
            fancy_times (bool): Whether to use fancy times.
            before (Optional[datetime.datetime]): The date to fetch messages before.
            after (Optional[datetime.datetime]): The date to fetch messages after.
            bot (Optional['discord.Client']): The bot to use for fetching members.
            attachment_handler (Optional[AttachmentHandler]): The attachment handler to use.
            tenor_api_key (Optional[str]): The Tenor API key to use.
        """
        self.channel = channel
        self.messages = messages
        self.limit = int(limit) if limit else None
        self.military_time = military_time
        self.fancy_times = fancy_times
        self.before = before
        self.after = after
        self.pytz_timezone = pytz_timezone
        self.attachment_handler = attachment_handler
        self.tenor_api_key = tenor_api_key
        self.bot = bot

    async def build_transcript(self) -> "TranscriptDAO":
        """Builds the transcript.

        Returns:
            TranscriptDAO: The TranscriptDAO object.
        """
        message_html, meta_data = await gather_messages(
            self.messages,
            self.channel.guild,
            self.pytz_timezone,
            self.military_time,
            self.attachment_handler,
            self.tenor_api_key,
            bot=self.bot,
        )
        await self.export_transcript(message_html, meta_data)
        clear_cache()
        Component.menu_div_id = 0
        return self

    async def export_transcript(self, message_html: str, meta_data: str) -> None:
        """Exports the transcript to HTML.

        Args:
            message_html (str): The HTML of the messages.
            meta_data (str): The metadata of the transcript.
        """
        guild_icon = (
            self.channel.guild.icon
            if (self.channel.guild.icon and len(self.channel.guild.icon) > 2)
            else DiscordUtils.default_avatar
        )

        guild_name = html.escape(self.channel.guild.name)

        timezone = pytz.timezone(self.pytz_timezone)
        if self.military_time:
            time_now = datetime.datetime.now(timezone).strftime(
                "%e %B %Y at %H:%M:%S (%Z)"
            )
        else:
            time_now = datetime.datetime.now(timezone).strftime(
                "%e %B %Y at %I:%M:%S %p (%Z)"
            )

        meta_data_html: str = ""
        for data in meta_data:
            creation_time = (
                meta_data[int(data)][1].astimezone(timezone).strftime("%b %d, %Y")
            )
            joined_time = (
                meta_data[int(data)][5].astimezone(timezone).strftime("%b %d, %Y")
                if meta_data[int(data)][5]
                else "Unknown"
            )

            pattern = r"^#\d{4}"
            discrim = str(meta_data[int(data)][0][-5:])
            user = str(meta_data[int(data)][0])

            meta_data_html += await fill_out(
                self.channel.guild,
                meta_data_temp,
                [
                    ("USER_ID", str(data), PARSE_MODE_NONE),
                    (
                        "USERNAME",
                        user[:-5] if re.match(pattern, discrim) else user,
                        PARSE_MODE_NONE,
                    ),
                    ("DISCRIMINATOR", discrim if re.match(pattern, discrim) else ""),
                    ("BOT", str(meta_data[int(data)][2]), PARSE_MODE_NONE),
                    ("CREATED_AT", str(creation_time), PARSE_MODE_NONE),
                    ("JOINED_AT", str(joined_time), PARSE_MODE_NONE),
                    ("GUILD_ICON", str(guild_icon), PARSE_MODE_NONE),
                    ("DISCORD_ICON", str(DiscordUtils.logo), PARSE_MODE_NONE),
                    ("MEMBER_ID", str(data), PARSE_MODE_NONE),
                    ("USER_AVATAR", str(meta_data[int(data)][3]), PARSE_MODE_NONE),
                    ("DISPLAY", str(meta_data[int(data)][6]), PARSE_MODE_NONE),
                    ("MESSAGE_COUNT", str(meta_data[int(data)][4])),
                ],
                bot=self.bot,
                timezone=self.pytz_timezone,
            )

        if self.military_time:
            channel_creation_time = self.channel.created_at.astimezone(
                timezone
            ).strftime("%b %d, %Y (%H:%M:%S)")
        else:
            channel_creation_time = self.channel.created_at.astimezone(
                timezone
            ).strftime("%b %d, %Y (%I:%M:%S %p)")

        raw_channel_topic = (
            self.channel.topic
            if isinstance(self.channel, discord.TextChannel) and self.channel.topic
            else ""
        )

        channel_topic_html = ""
        if raw_channel_topic:
            channel_topic_html = await fill_out(
                self.channel.guild,
                channel_topic,
                [("CHANNEL_TOPIC", html.escape(raw_channel_topic))],
                bot=self.bot,
                timezone=self.pytz_timezone,
            )

        limit = "start"
        if self.limit:
            limit = f"latest {self.limit} messages"

        subject = await fill_out(
            self.channel.guild,
            channel_subject,
            [
                ("LIMIT", limit, PARSE_MODE_NONE),
                ("CHANNEL_NAME", self.channel.name),
                ("RAW_CHANNEL_TOPIC", str(raw_channel_topic)),
            ],
            bot=self.bot,
            timezone=self.pytz_timezone,
        )

        _fancy_time = ""

        if self.fancy_times:
            time_format = "HH:mm" if self.military_time else "hh:mm A"

            _fancy_time = await fill_out(
                self.channel.guild,
                fancy_time,
                [
                    ("TIME_FORMAT", time_format, PARSE_MODE_NONE),
                    ("TIMEZONE", str(self.pytz_timezone), PARSE_MODE_NONE),
                ],
                bot=self.bot,
                timezone=self.pytz_timezone,
            )

        self.html = await fill_out(
            self.channel.guild,
            total,
            [
                ("SERVER_NAME", f"{guild_name}"),
                ("GUILD_ID", str(self.channel.guild.id), PARSE_MODE_NONE),
                ("SERVER_AVATAR_URL", str(guild_icon), PARSE_MODE_NONE),
                ("CHANNEL_NAME", f"{self.channel.name}"),
                ("MESSAGE_COUNT", str(len(self.messages))),
                ("MESSAGES", message_html, PARSE_MODE_NONE),
                ("META_DATA", meta_data_html, PARSE_MODE_NONE),
                ("DATE_TIME", str(time_now)),
                ("SUBJECT", subject, PARSE_MODE_NONE),
                ("CHANNEL_CREATED_AT", str(channel_creation_time), PARSE_MODE_NONE),
                ("CHANNEL_TOPIC", str(channel_topic_html), PARSE_MODE_NONE),
                ("CHANNEL_ID", str(self.channel.id), PARSE_MODE_NONE),
                ("MESSAGE_PARTICIPANTS", str(len(meta_data)), PARSE_MODE_NONE),
                ("FANCY_TIME", _fancy_time, PARSE_MODE_NONE),
                ("SERVER_NAME_SAFE", f"{guild_name}", PARSE_MODE_HTML_SAFE),
                (
                    "CHANNEL_NAME_SAFE",
                    f"{html.escape(self.channel.name)}",
                    PARSE_MODE_HTML_SAFE,
                ),
            ],
            bot=self.bot,
            timezone=self.pytz_timezone,
        )


class Transcript(TranscriptDAO):
    """A class to create a transcript of a Discord channel."""

    async def export(self) -> "TranscriptDAO":
        """Exports the transcript.

        Returns:
            TranscriptDAO: The TranscriptDAO object.
        """
        if not self.messages:
            self.messages = [
                message
                async for message in self.channel.history(
                    limit=self.limit,
                    before=self.before,
                    after=self.after,
                )
            ]

        if self.after is None:
            self.messages.reverse()

        try:
            return await super().build_transcript()
        except discord.errors.Forbidden:
            self.html = "Whoops! I don't have permission to see this channel."
            return self
        except discord.errors.HTTPException:
            self.html = "Whoops! Something went wrong while fetching the messages."
            return self
        except Exception:
            self.html = "Whoops! Something went wrong..."
            traceback.print_exc()
            print(
                "Please send a screenshot of the above error to https://github.com/Xougui/discord-channel-to-html-transcripts"
            )
            return self
