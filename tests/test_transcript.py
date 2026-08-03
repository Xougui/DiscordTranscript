import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from DiscordTranscript.construct.transcript import Transcript


@pytest.fixture
def mock_channel():
    channel = AsyncMock()
    channel.name = "test-channel"
    channel.guild = MagicMock()
    channel.created_at = datetime.datetime.now()
    channel.guild.icon = ""
    channel.guild.timezone = "UTC"
    return channel


def create_mock_message(content, created_at, edited_at=None):
    message = MagicMock()
    message.content = content
    message.created_at = created_at
    message.edited_at = edited_at
    message.author.name = "test"
    message.author.bot = False
    message.author.display_avatar = ""
    message.author.discriminator = "0001"
    message.author.id = 1
    message.author.display_name = "test"
    message.attachments = []
    message.embeds = []
    message.stickers = []
    message.reference = None
    message.components = []
    message.mentions = []
    message.channel_mentions = []
    message.role_mentions = []
    message.author.joined_at = datetime.datetime.now()
    return message


@pytest.mark.asyncio
async def test_message_order_with_before_only(mock_channel):
    """
    Test that messages are in the correct chronological order
    when using only the `before` parameter.
    """

    message1 = create_mock_message("message 1", datetime.datetime(2023, 1, 1, 12, 0, 0))
    message2 = create_mock_message("message 2", datetime.datetime(2023, 1, 1, 12, 1, 0))

    async def mock_history_generator():
        for msg in [message2, message1]:
            yield msg

    mock_channel.history = MagicMock(return_value=mock_history_generator())

    transcript = Transcript(
        channel=mock_channel,
        limit=None,
        messages=None,
        pytz_timezone="UTC",
        military_time=True,
        fancy_times=False,
        before=datetime.datetime(2023, 1, 1, 12, 2, 0),
        after=None,
        bot=None,
        attachment_handler=None,
    )

    await transcript.export()

    exported_messages = transcript.messages

    assert exported_messages is not None
    assert len(exported_messages) == 2
    assert exported_messages[0].created_at < exported_messages[1].created_at


@pytest.mark.asyncio
async def test_message_order_with_after_only(mock_channel):
    """
    Test that messages are in the correct chronological order
    when using only the `after` parameter.
    """
    message1 = create_mock_message("message 1", datetime.datetime(2023, 1, 1, 12, 0, 0))
    message2 = create_mock_message("message 2", datetime.datetime(2023, 1, 1, 12, 1, 0))

    async def mock_history_generator():
        for msg in [message1, message2]:
            yield msg

    mock_channel.history = MagicMock(return_value=mock_history_generator())

    transcript = Transcript(
        channel=mock_channel,
        limit=None,
        messages=None,
        pytz_timezone="UTC",
        military_time=True,
        fancy_times=False,
        before=None,
        after=datetime.datetime(2023, 1, 1, 11, 59, 0),
        bot=None,
        attachment_handler=None,
    )

    await transcript.export()

    exported_messages = transcript.messages

    assert exported_messages is not None
    assert len(exported_messages) == 2
    assert exported_messages[0].created_at < exported_messages[1].created_at


@pytest.mark.asyncio
async def test_message_order_with_before_and_after(mock_channel):
    """
    Test that messages are in the correct chronological order
    when using both `before` and `after` parameters.
    """
    message1 = create_mock_message("message 1", datetime.datetime(2023, 1, 1, 12, 0, 0))
    message2 = create_mock_message("message 2", datetime.datetime(2023, 1, 1, 12, 1, 0))

    async def mock_history_generator():
        for msg in [message1, message2]:
            yield msg

    mock_channel.history = MagicMock(return_value=mock_history_generator())

    transcript = Transcript(
        channel=mock_channel,
        limit=None,
        messages=None,
        pytz_timezone="UTC",
        military_time=True,
        fancy_times=False,
        before=datetime.datetime(2023, 1, 1, 12, 2, 0),
        after=datetime.datetime(2023, 1, 1, 11, 59, 0),
        bot=None,
        attachment_handler=None,
    )

    await transcript.export()

    exported_messages = transcript.messages

    assert exported_messages is not None
    assert len(exported_messages) == 2
    assert exported_messages[0].created_at < exported_messages[1].created_at


@pytest.mark.asyncio
async def test_attachment_data_uri_handler_image_optimization():
    import io

    from PIL import Image

    from DiscordTranscript.construct.attachment_handler import (
        AttachmentToDataURIHandler,
    )

    handler = AttachmentToDataURIHandler(optimize_images=True, max_image_dimension=100)

    # Create a dummy large image in memory (500x500 PNG)
    img = Image.new("RGB", (500, 500), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    raw_data = buf.getvalue()

    opt_data, opt_type = handler._optimize_image(raw_data, "image/png")
    assert len(opt_data) < len(raw_data)
    assert opt_type in ("image/jpeg", "image/webp")
