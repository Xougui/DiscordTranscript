import html
import math
from typing import TYPE_CHECKING, Optional

import aiohttp

from DiscordTranscript.ext.discord_utils import DiscordUtils
from DiscordTranscript.ext.html_generator import (
    PARSE_MODE_NONE,
    audio_attachment,
    fill_out,
    img_attachment,
    msg_attachment,
    text_attachment,
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
        language: str = "en",
    ):
        """Initializes the Attachment.

        Args:
            attachments (discord.Attachment): The attachment to represent.
            guild (discord.Guild): The guild the attachment is in.
            bot (Optional[discord.Client]): The bot instance. Defaults to None.
            timezone (str): The timezone to use. Defaults to "UTC".
            language (str): The language code. Defaults to "en".
        """
        self.attachments = attachments
        self.guild = guild
        self.bot = bot
        self.timezone = timezone
        self.language = language

    async def flow(self) -> str:
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
            elif self.is_text_attachment():
                return await self.text_file()
        if self.attachments.filename and self.attachments.filename.lower().endswith(
            ".gif"
        ):
            return await self.image()
        if self.is_text_attachment():
            return await self.text_file()
        await self.file()

    def is_text_attachment(self) -> bool:
        """Determines if the attachment is a text/code file eligible for inline preview."""
        filename = (self.attachments.filename or "").lower()
        content_type = (self.attachments.content_type or "").lower()

        if content_type.startswith("text/") or content_type in (
            "application/json",
            "application/javascript",
            "application/xml",
            "application/x-yaml",
            "application/yaml",
            "application/toml",
            "application/sql",
            "application/x-sh",
            "application/x-c",
            "application/x-python",
        ):
            return True

        text_extensions = (
            ".txt",
            ".log",
            ".html",
            ".htm",
            ".css",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".json",
            ".xml",
            ".csv",
            ".tsv",
            ".md",
            ".markdown",
            ".rst",
            ".py",
            ".pyw",
            ".c",
            ".cpp",
            ".h",
            ".hpp",
            ".cs",
            ".java",
            ".rs",
            ".go",
            ".php",
            ".rb",
            ".sh",
            ".bash",
            ".zsh",
            ".ps1",
            ".bat",
            ".cmd",
            ".yaml",
            ".yml",
            ".toml",
            ".ini",
            ".cfg",
            ".conf",
            ".env",
            ".sql",
            ".lua",
            ".r",
            ".dart",
            ".swift",
            ".kt",
            ".kts",
            ".asm",
            ".diff",
            ".patch",
        )
        return any(filename.endswith(ext) for ext in text_extensions)

    def is_code_attachment(self) -> bool:
        """Determines if the attachment is a code/markup file rather than plain text/log."""
        filename = (self.attachments.filename or "").lower()
        content_type = (self.attachments.content_type or "").lower()

        if content_type in (
            "application/json",
            "application/javascript",
            "application/xml",
            "application/x-yaml",
            "application/yaml",
            "application/toml",
            "application/sql",
            "application/x-sh",
            "application/x-c",
            "application/x-python",
            "text/html",
            "text/css",
            "text/javascript",
            "text/x-python",
            "text/x-c",
        ):
            return True

        code_extensions = (
            ".html",
            ".htm",
            ".css",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".json",
            ".xml",
            ".csv",
            ".tsv",
            ".py",
            ".pyw",
            ".c",
            ".cpp",
            ".h",
            ".hpp",
            ".cs",
            ".java",
            ".rs",
            ".go",
            ".php",
            ".rb",
            ".sh",
            ".bash",
            ".zsh",
            ".ps1",
            ".bat",
            ".cmd",
            ".yaml",
            ".yml",
            ".toml",
            ".ini",
            ".cfg",
            ".conf",
            ".env",
            ".sql",
            ".lua",
            ".r",
            ".dart",
            ".swift",
            ".kt",
            ".kts",
            ".asm",
            ".diff",
            ".patch",
        )
        return any(filename.endswith(ext) for ext in code_extensions)

    async def _fetch_text_content(self) -> str | None:
        """Fetches text content for inline preview."""
        # 1. Check if mock/attachment object already has text or content attribute
        for attr in ("text", "content", "raw_content"):
            val = getattr(self.attachments, attr, None)
            if isinstance(val, str):
                return val

        # 2. Check if attachment has read() method
        read_meth = getattr(self.attachments, "read", None)
        if callable(read_meth):
            try:
                import inspect

                if inspect.iscoroutinefunction(read_meth):
                    raw_data = await read_meth()
                else:
                    raw_data = read_meth()
                if isinstance(raw_data, bytes):
                    return raw_data.decode("utf-8", errors="replace")
                if isinstance(raw_data, str):
                    return raw_data
            except Exception:
                pass

        # 3. Check data URI
        url = self.attachments.proxy_url or self.attachments.url or ""
        if url.startswith("data:"):
            try:
                import base64

                header, encoded = url.split(",", 1)
                if ";base64" in header:
                    decoded = base64.b64decode(encoded)
                    return decoded.decode("utf-8", errors="replace")
                else:
                    import urllib.parse

                    return urllib.parse.unquote(encoded)
            except Exception:
                pass

        # 4. Try fetching via aiohttp if it's an HTTP URL (capped to 500KB)
        if url.startswith("http://") or url.startswith("https://"):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url, timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            data = await response.read()
                            if len(data) <= 500000:
                                return data.decode("utf-8", errors="replace")
            except Exception:
                pass

        return None

    async def text_file(self):
        """Builds an inline text preview attachment."""
        text_content = await self._fetch_text_content()
        if text_content is None:
            return await self.file()

        max_chars = 50000
        preview_content = (
            text_content[:max_chars] if len(text_content) > max_chars else text_content
        )
        escaped_content = html.escape(preview_content)
        file_size = self.get_file_size(self.attachments.size, language=self.language)
        rem_label = (
            f"... ({file_size} restants)"
            if self.language == "fr"
            else f"... ({file_size} remaining)"
        )
        rem_notice_html = f'<span class="chatlog__attachment-text-remaining-tag">{html.escape(rem_label)}</span>'
        extra_container_classes = (
            " chatlog__attachment-code-container" if self.is_code_attachment() else ""
        )
        extra_container_classes = (
            " chatlog__attachment-code-container" if self.is_code_attachment() else ""
        )

        self.attachments = await fill_out(
            self.guild,
            text_attachment,
            [
                ("ATTACH_URL", self.attachments.proxy_url, PARSE_MODE_NONE),
                ("ATTACH_BYTES", str(file_size), PARSE_MODE_NONE),
                ("ATTACH_FILE", str(self.attachments.filename), PARSE_MODE_NONE),
                ("ATTACH_TEXT_CONTENT", escaped_content, PARSE_MODE_NONE),
                ("ATTACH_REMAINING_NOTICE", rem_notice_html, PARSE_MODE_NONE),
                ("ATTACH_EXTRA_CLASSES", extra_container_classes, PARSE_MODE_NONE),
            ],
            bot=self.bot,
            timezone=self.timezone,
            language=self.language,
        )

    async def audio(self):
        """Builds an audio attachment."""
        file_icon = DiscordUtils.file_attachment_audio
        file_size = self.get_file_size(self.attachments.size, language=self.language)

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
            language=self.language,
        )

    async def file(self):
        """Builds a file attachment."""
        file_icon = await self.get_file_icon()
        file_size = self.get_file_size(self.attachments.size, language=self.language)

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
            language=self.language,
        )

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

    @staticmethod
    def get_file_size(file_size, language="en"):
        """Gets the file size in a human-readable format.

        Args:
            file_size (int): The size of the file in bytes.
            language (str): The language code ('fr', 'en', etc.).

        Returns:
            str: The file size in a human-readable format.
        """
        if file_size == 0:
            return "0 octets" if language == "fr" else "0 bytes"

        if language == "fr":
            size_name = ("octets", "Ko", "Mo", "Go")
        else:
            size_name = ("bytes", "KB", "MB", "GB")

        i = math.floor(math.log(file_size, 1024))
        i = min(i, len(size_name) - 1)
        p = math.pow(1024, i)
        val = file_size / p

        if i == 0:
            formatted_val = str(int(val))
        elif val >= 10:
            formatted_val = str(int(round(val)))
        else:
            formatted_val = f"{round(val, 1):.1f}".rstrip("0").rstrip(".")

        return f"{formatted_val} {size_name[i]}"

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
