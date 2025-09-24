from __future__ import annotations
import base64
import datetime
import io
import urllib.parse

import aiohttp
from DiscordTranscript.ext.discord_import import discord


class AttachmentHandler:
    """A base class for handling attachments.

    Subclass this to implement your own asset handler.
    """



    async def process_asset(self, attachment: discord.Attachment) -> discord.Attachment:
        """Processes an asset and returns a URL to the stored attachment.

        Args:
            attachment (discord.Attachment): The attachment to process.

        Returns:
            discord.Attachment: The processed attachment with a new URL.
        """
        raise NotImplementedError


class AttachmentToDataURIHandler(AttachmentHandler):
    """Saves assets to a data URI and embeds them in the transcript."""

    async def process_asset(self, attachment: discord.Attachment) -> discord.Attachment:
        """Saves an asset to a data URI and returns a new attachment.

        Args:
            attachment (discord.Attachment): The attachment to process.

        Returns:
            discord.Attachment: The processed attachment with a new URL.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as res:
                    if res.status != 200:
                        return attachment
                    data = await res.read()
                    encoded_data = base64.b64encode(data).decode("utf-8")
                    data_uri = f"data:{attachment.content_type};base64,{encoded_data}"
                    attachment.url = data_uri
                    attachment.proxy_url = data_uri
                    return attachment
        except Exception:
            return attachment


class AttachmentToDiscordChannelHandler(AttachmentHandler):
    """Saves an attachment to a Discord channel and embeds it in the transcript.

    Attributes:
        channel (discord.TextChannel): The channel to save attachments to.
    """



    def __init__(self, channel: discord.TextChannel):
        """Initializes the AttachmentToDiscordChannelHandler.

        Args:
            channel (discord.TextChannel): The channel to save attachments to.
        """
        self.channel = channel

    async def process_asset(self, attachment: discord.Attachment) -> discord.Attachment:
        """Saves an asset to the Discord channel and returns a new attachment.

        Args:
            attachment (discord.Attachment): The attachment to process.

        Returns:
            discord.Attachment: The processed attachment with a new URL.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as res:
                    if res.status != 200:
                        res.raise_for_status()
                    data = io.BytesIO(await res.read())
                    data.seek(0)
                    attach = discord.File(data, attachment.filename)
                    msg = await self.channel.send(file=attach)
                    return msg.attachments[0]
        except discord.errors.HTTPException as e:
            # discords http errors, including missing permissions
            raise e