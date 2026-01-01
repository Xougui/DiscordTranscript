import math
from typing import TYPE_CHECKING, Optional

from DiscordTranscript.ext.discord_utils import DiscordUtils
from DiscordTranscript.ext.html_generator import (
    PARSE_MODE_NONE,
    audio_attachment,
    fill_out,
    img_attachment,
    msg_attachment,
    video_attachment,
)

if TYPE_CHECKING:
    import discord as discord_typings


class Attachment:
    """A class to represent a Discord attachment.

    Attributes:
        attachments (discord.Attachment): The attachment to represent.
        guild (discord.Guild): The guild the attachment is in.
    """

    def __init__(
        self,
        attachments,
        guild,
        bot: Optional["discord_typings.Client"] = None,
        timezone: str = "UTC",
    ):
        """Initializes the Attachment.

        Args:
            attachments (discord.Attachment): The attachment to represent.
            guild (discord.Guild): The guild the attachment is in.
            bot (Optional[discord.Client]): The bot instance. Defaults to None.
            timezone (str): The timezone to use. Defaults to "UTC".
        """
        self.attachments = attachments
        self.guild = guild
        self.bot = bot
        self.timezone = timezone

    async def flow(self):
        """Builds the attachment and returns the HTML.

        Returns:
            str: The HTML of the attachment.
        """
        await self.build_attachment()
        return self.attachments

    async def build_attachment(self):
        """Builds the attachment's HTML based on its content type."""
        if self.attachments.content_type is not None:
            if "image" in self.attachments.content_type:
                return await self.image()
            elif "video" in self.attachments.content_type:
                return await self.video()
            elif "audio" in self.attachments.content_type:
                return await self.audio()
        if self.attachments.filename and self.attachments.filename.lower().endswith(
            ".gif"
        ):
            return await self.image()
        await self.file()

    async def image(self):
        """Builds an image attachment."""
        spoiler_classes = ""
        if self.attachments.filename.startswith("SPOILER_"):
            spoiler_classes = "spoiler spoiler-image spoiler--hidden"

        self.attachments = await fill_out(
            self.guild,
            img_attachment,
            [
                ("SPOILER_CLASSES", spoiler_classes, PARSE_MODE_NONE),
                ("ATTACH_URL", self.attachments.proxy_url, PARSE_MODE_NONE),
                ("ATTACH_URL_THUMB", self.attachments.proxy_url, PARSE_MODE_NONE),
            ],
            bot=self.bot,
            timezone=self.timezone,
        )

    async def video(self):
        """Builds a video attachment."""
        self.attachments = await fill_out(
            self.guild,
            video_attachment,
            [("ATTACH_URL", self.attachments.proxy_url, PARSE_MODE_NONE)],
            bot=self.bot,
            timezone=self.timezone,
        )

    async def audio(self):
        """Builds an audio attachment."""
        file_icon = DiscordUtils.file_attachment_audio
        file_size = self.get_file_size(self.attachments.size)

        self.attachments = await fill_out(
            self.guild,
            audio_attachment,
            [
                ("ATTACH_ICON", file_icon, PARSE_MODE_NONE),
                ("ATTACH_URL", self.attachments.proxy_url, PARSE_MODE_NONE),
                ("ATTACH_BYTES", str(file_size), PARSE_MODE_NONE),
                ("ATTACH_AUDIO", self.attachments.proxy_url, PARSE_MODE_NONE),
                ("ATTACH_FILE", str(self.attachments.filename), PARSE_MODE_NONE),
            ],
            bot=self.bot,
            timezone=self.timezone,
        )

    async def file(self):
        """Builds a file attachment."""
        file_icon = await self.get_file_icon()

        file_size = self.get_file_size(self.attachments.size)

        self.attachments = await fill_out(
            self.guild,
            msg_attachment,
            [
                ("ATTACH_ICON", file_icon, PARSE_MODE_NONE),
                ("ATTACH_URL", self.attachments.proxy_url, PARSE_MODE_NONE),
                ("ATTACH_BYTES", str(file_size), PARSE_MODE_NONE),
                ("ATTACH_FILE", str(self.attachments.filename), PARSE_MODE_NONE),
            ],
            bot=self.bot,
            timezone=self.timezone,
        )

    @staticmethod
    def get_file_size(file_size):
        """Gets the file size in a human-readable format.

        Args:
            file_size (int): The size of the file in bytes.

        Returns:
            str: The file size in a human-readable format.
        """
        if file_size == 0:
            return "0 bytes"
        size_name = ("bytes", "KB", "MB")
        i = int(math.floor(math.log(file_size, 1024)))
        p = math.pow(1024, i)
        s = round(file_size / p, 2)
        return "%s %s" % (s, size_name[i])

    async def get_file_icon(self) -> str:
        """Gets the file icon based on the file extension.

        Returns:
            str: The URL of the file icon.
        """
        acrobat_types = "pdf"
        webcode_types = "html", "htm", "css", "rss", "xhtml", "xml"
        code_types = (
            "py",
            "cgi",
            "pl",
            "gadget",
            "jar",
            "msi",
            "wsf",
            "bat",
            "php",
            "js",
        )
        document_types = (
            "txt",
            "doc",
            "docx",
            "rtf",
            "xls",
            "xlsx",
            "ppt",
            "pptx",
            "odt",
            "odp",
            "ods",
            "odg",
            "odf",
            "swx",
            "sxi",
            "sxc",
            "sxd",
            "stw",
        )
        archive_types = (
            "br",
            "rpm",
            "dcm",
            "epub",
            "zip",
            "tar",
            "rar",
            "gz",
            "bz2",
            "7x",
            "deb",
            "ar",
            "Z",
            "lzo",
            "lz",
            "lz4",
            "arj",
            "pkg",
            "z",
        )

        for tmp in [self.attachments.proxy_url, self.attachments.filename]:
            if not tmp:
                continue
            extension = tmp.rsplit(".", 1)[-1]
            if extension in acrobat_types:
                return DiscordUtils.file_attachment_acrobat
            elif extension in webcode_types:
                return DiscordUtils.file_attachment_webcode
            elif extension in code_types:
                return DiscordUtils.file_attachment_code
            elif extension in document_types:
                return DiscordUtils.file_attachment_document
            elif extension in archive_types:
                return DiscordUtils.file_attachment_archive

        return DiscordUtils.file_attachment_unknown
