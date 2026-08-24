from __future__ import annotations

import base64
import io
from typing import TYPE_CHECKING

import aiohttp

from DiscordTranscript.ext.discord_import import discord

try:
    from PIL import Image, ImageOps

    HAS_PIL = True
except ImportError:
    HAS_PIL = False

if TYPE_CHECKING:
    import discord as discord_typings


class AttachmentHandler:
    """A base class for handling attachments.

    Subclass this to implement your own asset handler.
    """

    async def process_asset(
        self, attachment: discord_typings.Attachment
    ) -> discord_typings.Attachment:
        """Processes an asset and returns a URL to the stored attachment.

        Args:
            attachment (discord.Attachment): The attachment to process.

        Returns:
            discord.Attachment: The processed attachment with a new URL.
        """
        raise NotImplementedError


class AttachmentToDataURIHandler(AttachmentHandler):
    """Saves assets to a data URI and embeds them in the transcript."""

    def __init__(
        self,
        session: aiohttp.ClientSession | None = None,
        only_expiring: bool = True,
        optimize_images: bool = True,
        max_image_dimension: int = 1280,
        quality: int = 80,
    ):
        """Initializes AttachmentToDataURIHandler.

        Args:
            session (Optional[aiohttp.ClientSession]): The shared HTTP session to use.
            only_expiring (bool): Whether to only convert expiring Discord URLs to Data URIs. Defaults to True.
            optimize_images (bool): Whether to resize and compress images before Base64 encoding. Defaults to True.
            max_image_dimension (int): Maximum width/height in pixels for compressed images. Defaults to 1280.
            quality (int): Compression quality (1-100) for JPEG/WebP images. Defaults to 80.
        """
        self.session = session
        self.only_expiring = only_expiring
        self.optimize_images = optimize_images
        self.max_image_dimension = max_image_dimension
        self.quality = quality
        self._cache: dict[str, str] = {}

    def is_expiring_url(self, url: str) -> bool:
        """Checks if a URL is a Discord expiring URL."""
        return (
            "ex=" in url
            or "cdn.discordapp.com/attachments/" in url
            or "media.discordapp.net/attachments/" in url
        )

    def _optimize_image(
        self, data: bytes, content_type: str | None
    ) -> tuple[bytes, str]:
        if not HAS_PIL or not self.optimize_images:
            return data, content_type or "application/octet-stream"

        try:
            with Image.open(io.BytesIO(data)) as img:
                if getattr(img, "is_animated", False):
                    return data, content_type or "image/gif"

                img = ImageOps.exif_transpose(img)

                if self.max_image_dimension:
                    img.thumbnail(
                        (self.max_image_dimension, self.max_image_dimension),
                        Image.Resampling.LANCZOS,
                    )

                output = io.BytesIO()
                if img.mode in ("RGBA", "LA") or (
                    img.mode == "P" and "transparency" in img.info
                ):
                    img.save(output, format="WEBP", quality=self.quality, method=4)
                    new_content_type = "image/webp"
                else:
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    img.save(output, format="JPEG", quality=self.quality, optimize=True)
                    new_content_type = "image/jpeg"

                optimized_bytes = output.getvalue()
                if len(optimized_bytes) < len(data):
                    return optimized_bytes, new_content_type
                return data, content_type or "image/jpeg"
        except Exception:
            return data, content_type or "application/octet-stream"

    async def process_asset(
        self, attachment: discord_typings.Attachment
    ) -> discord_typings.Attachment:
        """Saves an asset to a data URI and returns a new attachment.

        Args:
            attachment (discord.Attachment): The attachment to process.

        Returns:
            discord.Attachment: The processed attachment with a new URL.
        """
        if self.only_expiring and not self.is_expiring_url(attachment.url):
            return attachment

        if attachment.url in self._cache:
            data_uri = self._cache[attachment.url]
            attachment.url = data_uri
            attachment.proxy_url = data_uri
            return attachment

        try:
            close_session = False
            session = self.session
            if session is None:
                session = aiohttp.ClientSession()
                close_session = True

            try:
                async with session.get(attachment.url) as res:
                    if res.status != 200:
                        return attachment
                    data = await res.read()
                    content_type = attachment.content_type
                    if content_type and content_type.startswith("image/"):
                        data, content_type = self._optimize_image(data, content_type)
                    encoded_data = base64.b64encode(data).decode("utf-8")
                    data_uri = f"data:{content_type};base64,{encoded_data}"
                    self._cache[attachment.url] = data_uri
                    attachment.url = data_uri
                    attachment.proxy_url = data_uri
                    return attachment
            finally:
                if close_session:
                    await session.close()
        except Exception:
            return attachment


class AttachmentToDiscordChannelHandler(AttachmentHandler):
    """Saves an attachment to a Discord channel and embeds it in the transcript.

    Attributes:
        channel (discord.TextChannel): The channel to save attachments to.
    """

    def __init__(
        self,
        channel: discord_typings.TextChannel,
        session: aiohttp.ClientSession | None = None,
    ):
        """Initializes the AttachmentToDiscordChannelHandler.

        Args:
            channel (discord.TextChannel): The channel to save attachments to.
            session (Optional[aiohttp.ClientSession]): The shared HTTP session to use.
        """
        self.channel = channel
        self.session = session

    async def process_asset(
        self, attachment: discord_typings.Attachment
    ) -> discord_typings.Attachment:
        """Saves an asset to the Discord channel and returns a new attachment.

        Args:
            attachment (discord.Attachment): The attachment to process.

        Returns:
            discord.Attachment: The processed attachment with a new URL.
        """
        try:
            close_session = False
            session = self.session
            if session is None:
                session = aiohttp.ClientSession()
                close_session = True

            try:
                async with session.get(attachment.url) as res:
                    if res.status != 200:
                        res.raise_for_status()
                    data = io.BytesIO(await res.read())
                    data.seek(0)
                    attach = discord.File(data, attachment.filename)
                    msg = await self.channel.send(file=attach)
                    return msg.attachments[0]
            finally:
                if close_session:
                    await session.close()
        except Exception as e:
            if type(e).__name__ == "HTTPException":
                raise e
            return attachment
