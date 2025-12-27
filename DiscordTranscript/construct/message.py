from __future__ import annotations
import html
import re
import aiohttp
from typing import List, Optional, Tuple, TYPE_CHECKING
from datetime import timedelta
from pytz import timezone

from DiscordTranscript.construct.attachment_handler import AttachmentHandler
from DiscordTranscript.ext.discord_import import discord
from DiscordTranscript.construct.assets import Attachment, Component, Embed, Reaction
from DiscordTranscript.ext.discord_utils import DiscordUtils
from DiscordTranscript.ext.discriminator import discriminator
from DiscordTranscript.ext.cache import cache
from DiscordTranscript.ext.html_generator import (
    fill_out,
    bot_tag,
    bot_tag_verified,
    message_body,
    message_pin,
    message_thread,
    message_content,
    message_reference,
    message_reference_unknown,
    message_interaction,
    img_attachment,
    start_message,
    end_message,
    PARSE_MODE_NONE,
    PARSE_MODE_MARKDOWN,
    PARSE_MODE_REFERENCE,
    message_thread_remove,
    message_thread_add,
)

if TYPE_CHECKING:
    import discord as discord_typings


def _gather_user_bot(author: discord.Member):
def _gather_user_bot(author: discord_typings.Member):
    if author.bot and author.public_flags.verified_bot:
        return bot_tag_verified
    elif author.bot:
        return bot_tag
    return ""


def _set_edit_at(message_edited_at):
    return f'<span class="chatlog__reference-edited-timestamp" data-timestamp="{message_edited_at}">(edited)</span>'


class MessageConstruct:
    """A class to construct a single message's HTML.

    Attributes:
        message (discord.Message): The message to construct.
        previous_message (Optional[discord.Message]): The previous message in the channel.
        pytz_timezone (str): The timezone to use for timestamps.
        military_time (bool): Whether to use military time.
        guild (discord.Guild): The guild the channel belongs to.
        message_dict (dict): A dictionary of all messages in the channel.
        attachment_handler (Optional[AttachmentHandler]): The attachment handler to use.
        tenor_api_key (Optional[str]): The Tenor API key to use for fetching GIFs.
        processed_tenor_links (List[str]): A list of Tenor links that have already been processed.
        time_format (str): The format to use for timestamps.
        message_created_at (str): The message's creation time.
        message_edited_at (str): The message's edit time.
        meta_data (dict): A dictionary of metadata for the transcript.
        message_html (str): The HTML for the message.
        embeds (str): The HTML for the message's embeds.
        reactions (str): The HTML for the message's reactions.
        components (str): The HTML for the message's components.
        attachments (str): The HTML for the message's attachments.
        interaction (str): The HTML for the message's interaction.
        bot (Optional[discord.Client]): The bot instance.
    """

    message_html: str = ""

    # Asset Types
    embeds: str = ""
    reactions: str = ""
    components: str = ""
    attachments: str = ""
    time_format: str = ""

    interaction: str = ""

    def __init__(
        self,
        message: discord.Message,
        previous_message: Optional[discord.Message],
        message: discord_typings.Message,
        previous_message: Optional[discord_typings.Message],
        pytz_timezone,
        military_time: bool,
        guild: discord.Guild,
        guild: discord_typings.Guild,
        meta_data: dict,
        message_dict: dict,
        attachment_handler: Optional[AttachmentHandler],
        tenor_api_key: Optional[str] = None,
        bot: Optional["discord_typings.Client"] = None,
    ):
        """Initializes the MessageConstruct.

        Args:
            message (discord.Message): The message to construct.
            previous_message (Optional[discord.Message]): The previous message in the channel.
            pytz_timezone (str): The timezone to use for timestamps.
            military_time (bool): Whether to use military time.
            guild (discord.Guild): The guild the channel belongs to.
            meta_data (dict): A dictionary of metadata for the transcript.
            message_dict (dict): A dictionary of all messages in the channel.
            attachment_handler (Optional[AttachmentHandler]): The attachment handler to use.
            tenor_api_key (Optional[str]): The Tenor API key to use for fetching GIFs.
            bot (Optional[discord.Client]): The bot instance.
        """
        self.message = message
        self.previous_message = previous_message
        self.pytz_timezone = pytz_timezone
        self.military_time = military_time
        self.guild = guild
        self.message_dict = message_dict
        self.attachment_handler = attachment_handler
        self.tenor_api_key = tenor_api_key
        self.processed_tenor_links = []
        self.bot = bot
        self.time_format = "%A, %e %B %Y %I:%M %p"
        if self.military_time:
            self.time_format = "%A, %e %B %Y %H:%M"

        self.message_created_at, self.message_edited_at = self.set_time()
        self.meta_data = meta_data

    async def construct_message(
        self,
    ) -> Tuple[str, dict]:
        """Constructs the HTML for the message.

        Returns:
            Tuple[str, dict]: A tuple containing the message's HTML and the transcript's metadata.
        """
        if discord.MessageType.pins_add == self.message.type:
            await self.build_pin()
        elif discord.MessageType.thread_created == self.message.type:
            await self.build_thread()
        elif discord.MessageType.recipient_remove == self.message.type:
            await self.build_thread_remove()
        elif discord.MessageType.recipient_add == self.message.type:
            await self.build_thread_add()
        else:
            await self.build_message()
        return self.message_html, self.meta_data

    async def build_message(self):
        """Builds the HTML for a regular message."""
        await self.build_content()
        await self.build_reference()
        await self.build_interaction()
        await self.build_sticker()
        await self.build_assets()
        await self.build_message_template()
        await self.build_meta_data()

    async def build_pin(self):
        """Builds the HTML for a message pin."""
        await self.generate_message_divider(channel_audit=True)
        await self.build_pin_template()

    async def build_thread(self):
        """Builds the HTML for a thread creation message."""
        await self.generate_message_divider(channel_audit=True)
        await self.build_thread_template()

    async def build_thread_remove(self):
        """Builds the HTML for a thread remove message."""
        await self.generate_message_divider(channel_audit=True)
        await self.build_remove()

    async def build_thread_add(self):
        """Builds the HTML for a thread add message."""
        await self.generate_message_divider(channel_audit=True)
        await self.build_add()

    async def build_meta_data(self):
        """Builds the metadata for the transcript."""
        user_id = self.message.author.id

        if user_id in self.meta_data:
            self.meta_data[user_id][4] += 1
        else:
            user_name_discriminator = await discriminator(
                self.message.author.name, self.message.author.discriminator
            )
            user_created_at = self.message.author.created_at
            user_bot = _gather_user_bot(self.message.author)
            user_avatar = (
                self.message.author.display_avatar
                if self.message.author.display_avatar
                else DiscordUtils.default_avatar
            )
            user_joined_at = (
                self.message.author.joined_at
                if hasattr(self.message.author, "joined_at")
                else None
            )
            user_display_name = (
                f'<div class="meta__display-name">{html.escape(self.message.author.display_name)}</div>'
                if self.message.author.display_name != self.message.author.name
                else ""
            )
            self.meta_data[user_id] = [
                user_name_discriminator,
                user_created_at,
                user_bot,
                user_avatar,
                1,
                user_joined_at,
                user_display_name,
            ]

    async def build_content(self):
        """Builds the HTML for the message's content."""
        if not self.message.content:
            self.message.content = ""
            return

        content = self.message.content
        placeholders = {}

        if self.tenor_api_key and "tenor.com/view" in content:
            async with aiohttp.ClientSession() as session:
                links = [word for word in content.split() if "tenor.com/view" in word]
                for i, link in enumerate(links):
                    gif_url = await _process_tenor_link(
                        session, self.tenor_api_key, link
                    )
                    if gif_url:
                        placeholder = f"TENORGIFPLACEHOLDER{i}"
                        placeholders[placeholder] = (
                            f'<img src="{gif_url}" alt="GIF from Tenor" style="max-width: 100%;">'
                        )
                        content = content.replace(link, placeholder)
                        self.processed_tenor_links.append(link)

        if self.message_edited_at:
            self.message_edited_at = _set_edit_at(self.message_edited_at)

        self.message.content = html.escape(content).replace("&#96;", "`")

        self.message.content = await fill_out(
            self.guild,
            message_content,
            [
                ("MESSAGE_CONTENT", self.message.content, PARSE_MODE_MARKDOWN),
                ("EDIT", self.message_edited_at, PARSE_MODE_NONE),
            ],
            placeholders=placeholders,
            bot=self.bot,
            timezone=self.pytz_timezone,
        )

    async def build_reference(self):
        """Builds the HTML for a message reference."""
        if not self.message.reference:
            self.message.reference = ""
            return

        message: discord.Message = self.message_dict.get(
        message: discord_typings.Message = self.message_dict.get(
            self.message.reference.message_id
        )

        if not message:
            try:
                message: discord.Message = await self.message.channel.fetch_message(
                message: discord_typings.Message = await self.message.channel.fetch_message(
                    self.message.reference.message_id
                )
            except (discord.NotFound, discord.HTTPException) as e:
                self.message.reference = ""
                if isinstance(e, discord.NotFound):
                    self.message.reference = message_reference_unknown
                return

        is_bot = _gather_user_bot(message.author)
        user_colour = await self._gather_user_colour(message.author)

        icon = ""
        dummy = ""

        def get_interaction_status(interaction_message):
            if hasattr(interaction_message, "interaction_metadata"):
                return interaction_message.interaction_metadata
            return interaction_message.interaction

        interaction_status = get_interaction_status(message)
        if not interaction_status and (message.embeds or message.attachments):
            icon = DiscordUtils.reference_attachment_icon
            dummy = "Click to see attachment"
        elif interaction_status:
            icon = DiscordUtils.interaction_command_icon
            dummy = "Click to see command"

        if not message.content:
            message.content = dummy

        _, message_edited_at = self.set_time(message)

        if message_edited_at:
            message_edited_at = _set_edit_at(message_edited_at)

        avatar_url = (
            message.author.display_avatar
            if message.author.display_avatar
            else DiscordUtils.default_avatar
        )
        self.message.reference = await fill_out(
            self.guild,
            message_reference,
            [
                ("AVATAR_URL", str(avatar_url), PARSE_MODE_NONE),
                ("BOT_TAG", is_bot, PARSE_MODE_NONE),
                (
                    "NAME_TAG",
                    await discriminator(
                        message.author.name, message.author.discriminator
                    ),
                    PARSE_MODE_NONE,
                ),
                ("NAME", str(html.escape(message.author.display_name))),
                ("USER_COLOUR", user_colour, PARSE_MODE_NONE),
                (
                    "CONTENT",
                    message.content.replace("\n", "").replace("<br>", ""),
                    PARSE_MODE_REFERENCE,
                ),
                ("EDIT", message_edited_at, PARSE_MODE_NONE),
                ("ICON", icon, PARSE_MODE_NONE),
                ("USER_ID", str(message.author.id), PARSE_MODE_NONE),
                ("MESSAGE_ID", str(self.message.reference.message_id), PARSE_MODE_NONE),
            ],
            bot=self.bot,
            timezone=self.pytz_timezone,
        )

    async def build_interaction(self):
        """Builds the HTML for a message interaction."""
        if hasattr(self.message, "interaction_metadata"):
            if not self.message.interaction_metadata:
                self.interaction = ""
                return
            command = "a slash command"
            user = self.message.interaction_metadata.user
            interaction_id = self.message.interaction_metadata.id
        elif self.message.interaction:
            command = f"/{self.message.interaction.name}"
            user = self.message.interaction.user
            interaction_id = self.message.interaction.id
        else:
            self.interaction = ""
            return

        is_bot = _gather_user_bot(user)
        user_colour = await self._gather_user_colour(user)
        avatar_url = (
            user.display_avatar if user.display_avatar else DiscordUtils.default_avatar
        )

        self.interaction = await fill_out(
            self.guild,
            message_interaction,
            [
                ("AVATAR_URL", str(avatar_url), PARSE_MODE_NONE),
                ("BOT_TAG", is_bot, PARSE_MODE_NONE),
                (
                    "NAME_TAG",
                    await discriminator(user.name, user.discriminator),
                    PARSE_MODE_NONE,
                ),
                ("NAME", str(html.escape(user.display_name))),
                ("COMMAND", str(command), PARSE_MODE_NONE),
                ("USER_COLOUR", user_colour, PARSE_MODE_NONE),
                ("FILLER", "used ", PARSE_MODE_NONE),
                ("USER_ID", str(user.id), PARSE_MODE_NONE),
                ("INTERACTION_ID", str(interaction_id), PARSE_MODE_NONE),
            ],
            bot=self.bot,
            timezone=self.pytz_timezone,
        )

    async def build_sticker(self):
        """Builds the HTML for a message sticker."""
        if not self.message.stickers or not hasattr(self.message.stickers[0], "url"):
            return

        sticker_image_url = self.message.stickers[0].url

        if sticker_image_url.endswith(".json"):
            sticker = await self.message.stickers[0].fetch()
            sticker_image_url = f"https://cdn.jsdelivr.net/gh/mahtoid/DiscordUtils@master/stickers/{sticker.pack_id}/{sticker.id}.gif"

        self.message.content = await fill_out(
            self.guild,
            img_attachment,
            [
                ("SPOILER_CLASSES", "", PARSE_MODE_NONE),
                ("ATTACH_URL", str(sticker_image_url), PARSE_MODE_NONE),
                ("ATTACH_URL_THUMB", str(sticker_image_url), PARSE_MODE_NONE),
            ],
            bot=self.bot,
            timezone=self.pytz_timezone,
        )

    async def build_assets(self):
        """Builds the HTML for the message's assets (embeds, attachments, components, reactions)."""
        if self.processed_tenor_links:
            self.message.embeds = [
                embed
                for embed in self.message.embeds
                if not (embed.url and embed.url in self.processed_tenor_links)
            ]

        for e in self.message.embeds:
            self.embeds += await Embed(
                e, self.guild, bot=self.bot, timezone=self.pytz_timezone
            ).flow()

        for a in self.message.attachments:
            if self.attachment_handler and isinstance(
                self.attachment_handler, AttachmentHandler
            ):
                a = await self.attachment_handler.process_asset(a)
            self.attachments += await Attachment(
                a, self.guild, bot=self.bot, timezone=self.pytz_timezone
            ).flow()

        for c in self.message.components:
            self.components += await Component(
                c, self.guild, bot=self.bot, timezone=self.pytz_timezone
            ).flow()

        for r in self.message.reactions:
            self.reactions += await Reaction(
                r, self.guild, bot=self.bot, timezone=self.pytz_timezone
            ).flow()

        if self.reactions:
            self.reactions = f'<div class="chatlog__reactions">{self.reactions}</div>'

    async def build_message_template(self):
        """Builds the HTML for the message's template."""
        started = await self.generate_message_divider()

        if started:
            return self.message_html

        self.message_html += await fill_out(
            self.guild,
            message_body,
            [
                ("MESSAGE_ID", str(self.message.id)),
                ("MESSAGE_CONTENT", self.message.content, PARSE_MODE_NONE),
                ("EMBEDS", self.embeds, PARSE_MODE_NONE),
                ("ATTACHMENTS", self.attachments, PARSE_MODE_NONE),
                ("COMPONENTS", self.components, PARSE_MODE_NONE),
                ("EMOJI", self.reactions, PARSE_MODE_NONE),
                ("TIMESTAMP", self.message_created_at, PARSE_MODE_NONE),
                ("TIME", self.message_created_at.split(maxsplit=4)[4], PARSE_MODE_NONE),
            ],
            bot=self.bot,
            timezone=self.pytz_timezone,
        )

        return self.message_html

    def _generate_message_divider_check(self):
        """Checks if a message divider should be generated."""
        return bool(
            self.previous_message is None
            or self.message.reference != ""
            or self.previous_message.type is not discord.MessageType.default
            or self.interaction != ""
            or self.previous_message.author.id != self.message.author.id
            or self.message.webhook_id is not None
            or self.message.created_at
            > (self.previous_message.created_at + timedelta(minutes=4))
        )

    async def generate_message_divider(self, channel_audit=False):
        """Generates a message divider if necessary.

        Args:
            channel_audit (bool): Whether the message is a channel audit message.

        Returns:
            bool: Whether a message divider was generated.
        """
        if channel_audit or self._generate_message_divider_check():
            if self.previous_message is not None:
                self.message_html += await fill_out(
                    self.guild,
                    end_message,
                    [],
                    bot=self.bot,
                    timezone=self.pytz_timezone,
                )

            if channel_audit:
                self.audit = True
                return

            followup_symbol = ""
            is_bot = _gather_user_bot(self.message.author)
            avatar_url = (
                self.message.author.display_avatar
                if self.message.author.display_avatar
                else DiscordUtils.default_avatar
            )

            if self.message.reference != "" or self.interaction:
                followup_symbol = "<div class='chatlog__followup-symbol'></div>"

            time = self.message.created_at
            if not self.message.created_at.tzinfo:
                time = timezone("UTC").localize(time)

            if self.military_time:
                default_timestamp = time.astimezone(
                    timezone(self.pytz_timezone)
                ).strftime("%d-%m-%Y %H:%M")
            else:
                default_timestamp = time.astimezone(
                    timezone(self.pytz_timezone)
                ).strftime("%d-%m-%Y %I:%M %p")

            self.message_html += await fill_out(
                self.guild,
                start_message,
                [
                    ("REFERENCE_SYMBOL", followup_symbol, PARSE_MODE_NONE),
                    (
                        "REFERENCE",
                        self.message.reference
                        if self.message.reference
                        else self.interaction,
                        PARSE_MODE_NONE,
                    ),
                    ("AVATAR_URL", str(avatar_url), PARSE_MODE_NONE),
                    (
                        "NAME_TAG",
                        await discriminator(
                            self.message.author.name, self.message.author.discriminator
                        ),
                        PARSE_MODE_NONE,
                    ),
                    ("USER_ID", str(self.message.author.id)),
                    (
                        "USER_COLOUR",
                        await self._gather_user_colour(self.message.author),
                    ),
                    (
                        "USER_ICON",
                        await self._gather_user_icon(self.message.author),
                        PARSE_MODE_NONE,
                    ),
                    ("NAME", str(html.escape(self.message.author.display_name))),
                    ("BOT_TAG", str(is_bot), PARSE_MODE_NONE),
                    ("TIMESTAMP", str(self.message_created_at)),
                    ("DEFAULT_TIMESTAMP", str(default_timestamp), PARSE_MODE_NONE),
                    ("MESSAGE_ID", str(self.message.id)),
                    ("MESSAGE_CONTENT", self.message.content, PARSE_MODE_NONE),
                    ("EMBEDS", self.embeds, PARSE_MODE_NONE),
                    ("ATTACHMENTS", self.attachments, PARSE_MODE_NONE),
                    ("COMPONENTS", self.components, PARSE_MODE_NONE),
                    ("EMOJI", self.reactions, PARSE_MODE_NONE),
                ],
                bot=self.bot,
                timezone=self.pytz_timezone,
            )

            return True

    async def build_pin_template(self):
        """Builds the HTML for a message pin."""
        self.message_html += await fill_out(
            self.guild,
            message_pin,
            [
                ("PIN_URL", DiscordUtils.pinned_message_icon, PARSE_MODE_NONE),
                ("USER_COLOUR", await self._gather_user_colour(self.message.author)),
                ("NAME", str(html.escape(self.message.author.display_name))),
                (
                    "NAME_TAG",
                    await discriminator(
                        self.message.author.name, self.message.author.discriminator
                    ),
                    PARSE_MODE_NONE,
                ),
                ("MESSAGE_ID", str(self.message.id), PARSE_MODE_NONE),
                (
                    "REF_MESSAGE_ID",
                    str(self.message.reference.message_id)
                    if self.message.reference
                    else "",
                    PARSE_MODE_NONE,
                ),
            ],
            bot=self.bot,
            timezone=self.pytz_timezone,
        )

    async def build_thread_template(self):
        """Builds the HTML for a thread creation message."""
        self.message_html += await fill_out(
            self.guild,
            message_thread,
            [
                ("THREAD_URL", DiscordUtils.thread_channel_icon, PARSE_MODE_NONE),
                ("THREAD_NAME", html.escape(self.message.content), PARSE_MODE_NONE),
                ("USER_COLOUR", await self._gather_user_colour(self.message.author)),
                ("NAME", str(html.escape(self.message.author.display_name))),
                (
                    "NAME_TAG",
                    await discriminator(
                        self.message.author.name, self.message.author.discriminator
                    ),
                    PARSE_MODE_NONE,
                ),
                ("MESSAGE_ID", str(self.message.id), PARSE_MODE_NONE),
            ],
            bot=self.bot,
            timezone=self.pytz_timezone,
        )

    async def build_remove(self):
        """Builds the HTML for a message about a user being removed from a thread."""
        removed_member: discord.Member = self.message.mentions[0]
        removed_member: discord_typings.Member = self.message.mentions[0]
        self.message_html += await fill_out(
            self.guild,
            message_thread_remove,
            [
                ("THREAD_URL", DiscordUtils.thread_remove_recipient, PARSE_MODE_NONE),
                ("USER_COLOUR", await self._gather_user_colour(self.message.author)),
                ("NAME", str(html.escape(self.message.author.display_name))),
                (
                    "NAME_TAG",
                    await discriminator(
                        self.message.author.name, self.message.author.discriminator
                    ),
                    PARSE_MODE_NONE,
                ),
                (
                    "RECIPIENT_USER_COLOUR",
                    await self._gather_user_colour(removed_member),
                ),
                ("RECIPIENT_NAME", str(html.escape(removed_member.display_name))),
                (
                    "RECIPIENT_NAME_TAG",
                    await discriminator(
                        removed_member.name, removed_member.discriminator
                    ),
                    PARSE_MODE_NONE,
                ),
                ("MESSAGE_ID", str(self.message.id), PARSE_MODE_NONE),
            ],
            bot=self.bot,
            timezone=self.pytz_timezone,
        )

    async def build_add(self):
        """Builds the HTML for a message about a user being added to a thread."""
        removed_member: discord.Member = self.message.mentions[0]
        removed_member: discord_typings.Member = self.message.mentions[0]
        self.message_html += await fill_out(
            self.guild,
            message_thread_add,
            [
                ("THREAD_URL", DiscordUtils.thread_add_recipient, PARSE_MODE_NONE),
                ("USER_COLOUR", await self._gather_user_colour(self.message.author)),
                ("NAME", str(html.escape(self.message.author.display_name))),
                (
                    "NAME_TAG",
                    await discriminator(
                        self.message.author.name, self.message.author.discriminator
                    ),
                    PARSE_MODE_NONE,
                ),
                (
                    "RECIPIENT_USER_COLOUR",
                    await self._gather_user_colour(removed_member),
                ),
                ("RECIPIENT_NAME", str(html.escape(removed_member.display_name))),
                (
                    "RECIPIENT_NAME_TAG",
                    await discriminator(
                        removed_member.name, removed_member.discriminator
                    ),
                    PARSE_MODE_NONE,
                ),
                ("MESSAGE_ID", str(self.message.id), PARSE_MODE_NONE),
            ],
            bot=self.bot,
            timezone=self.pytz_timezone,
        )

    @cache()
    async def _gather_member(self, author: discord.Member):
    async def _gather_member(self, author: discord_typings.Member):
        """Gathers a member from the guild.

        Args:
            author (discord.Member): The member to gather.

        Returns:
            Optional[discord.Member]: The gathered member, or None if not found.
        """
        member = self.guild.get_member(author.id)

        if member:
            return member

        try:
            return await self.guild.fetch_member(author.id)
        except Exception:
            return None

    async def _gather_user_colour(self, author: discord.Member):
    async def _gather_user_colour(self, author: discord_typings.Member):
        """Gathers a user's colour.

        Args:
            author (discord.Member): The user to gather the colour from.

        Returns:
            str: The user's colour.
        """
        member = await self._gather_member(author)
        user_colour = (
            member.colour if member and str(member.colour) != "#000000" else "#FFFFFF"
        )
        return f"color: {user_colour};"

    async def _gather_user_icon(self, author: discord.Member):
    async def _gather_user_icon(self, author: discord_typings.Member):
        """Gathers a user's icon.

        Args:
            author (discord.Member): The user to gather the icon from.

        Returns:
            str: The user's icon.
        """
        member = await self._gather_member(author)

        if not member:
            return ""

        if hasattr(member, "display_icon") and member.display_icon:
            return f"<img class='chatlog__role-icon' src='{member.display_icon}' alt='Role Icon'>"
        elif hasattr(member, "top_role") and member.top_role and member.top_role.icon:
            return f"<img class='chatlog__role-icon' src='{member.top_role.icon}' alt='Role Icon'>"
        return ""

    def set_time(self, message: Optional[discord.Message] = None) -> Tuple[str, str]:
    def set_time(self, message: Optional[discord_typings.Message] = None) -> Tuple[str, str]:
        """Sets the time for a message.

        Args:
            message (Optional[discord.Message]): The message to set the time for. Defaults to None.

        Returns:
            Tuple[str, str]: A tuple containing the created_at and edited_at times.
        """
        message = message if message else self.message
        created_at_str = self.to_local_time_str(message.created_at)
        edited_at_str = (
            self.to_local_time_str(message.edited_at) if message.edited_at else ""
        )

        return created_at_str, edited_at_str

    def to_local_time_str(self, time) -> str:
        """Converts a time to a local time string.

        Args:
            time: The time to convert.

        Returns:
            str: The converted time.
        """
        if not self.message.created_at.tzinfo:
            time = timezone("UTC").localize(time)

        local_time = time.astimezone(timezone(self.pytz_timezone))

        return local_time.strftime(self.time_format)


async def _process_tenor_link(
    session: aiohttp.ClientSession, tenor_api_key: str, link: str
) -> Optional[str]:
    """Processes a Tenor link and returns the direct GIF URL.

    Args:
        session (aiohttp.ClientSession): The aiohttp client session.
        tenor_api_key (str): The Tenor API key.
        link (str): The Tenor link to process.

    Returns:
        Optional[str]: The direct GIF URL, or None if not found.
    """
    tenor_regex = r"https?:\/\/tenor\.com\/view\/[a-zA-Z0-9\-%]+\-([0-9]{16,20})"
    match = re.search(tenor_regex, link)
    if not match:
        return None

    gif_id = match.group(1)
    if not gif_id:
        return None

    url = f"https://tenor.googleapis.com/v2/posts?ids={gif_id}&key={tenor_api_key}&media_filter=gif"

    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data and "results" in data and data["results"]:
                    gif_url = data["results"][0]["media_formats"]["gif"]["url"]
                    return gif_url
            return None
    except Exception:
        return None


async def gather_messages(
    messages: List[discord.Message],
    guild: discord.Guild,
    messages: List[discord_typings.Message],
    guild: discord_typings.Guild,
    pytz_timezone,
    military_time,
    attachment_handler: Optional[AttachmentHandler],
    tenor_api_key: Optional[str] = None,
    bot: Optional["discord_typings.Client"] = None,
) -> Tuple[str, dict]:
    """Gathers all messages in a channel and returns the HTML and metadata.

    Args:
        messages (List[discord.Message]): The messages to gather.
        guild (discord.Guild): The guild the channel belongs to.
        pytz_timezone (str): The timezone to use for timestamps.
        military_time (bool): Whether to use military time.
        attachment_handler (Optional[AttachmentHandler]): The attachment handler to use.
        tenor_api_key (Optional[str]): The Tenor API key to use for fetching GIFs.
        bot (Optional[discord.Client]): The bot instance.

    Returns:
        Tuple[str, dict]: A tuple containing the HTML and metadata.
    """
    message_html: str = ""
    meta_data: dict = {}
    previous_message: Optional[discord.Message] = None
    previous_message: Optional[discord_typings.Message] = None

    message_dict = {message.id: message for message in messages}

    if messages and "thread" in str(messages[0].channel.type) and messages[0].reference:
        channel = guild.get_channel(messages[0].reference.channel_id)

        if not channel:
            channel = await guild.fetch_channel(messages[0].reference.channel_id)

        message = await channel.fetch_message(messages[0].reference.message_id)
        messages[0] = message
        messages[0].reference = None

    for message in messages:
        mc = MessageConstruct(
            message,
            previous_message,
            pytz_timezone,
            military_time,
            guild,
            meta_data,
            message_dict,
            attachment_handler,
            tenor_api_key=tenor_api_key,
            bot=bot,
        )
        content_html, meta_data = await mc.construct_message()

        message_html += content_html
        previous_message = message

    message_html += "</div>"
    return message_html, meta_data
