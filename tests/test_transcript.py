import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import datetime

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
    # Create mock messages with specific creation dates
    message1 = create_mock_message("message 1", datetime.datetime(2023, 1, 1, 12, 0, 0))
    message2 = create_mock_message("message 2", datetime.datetime(2023, 1, 1, 12, 1, 0))

    # The `history` method returns messages in reverse chronological order
    async def mock_history_generator():
        for msg in [message2, message1]:
            yield msg
    mock_channel.history = MagicMock(return_value=mock_history_generator())

    # Create a Transcript instance with a `before` date
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

    # Get the messages that were passed to build_transcript
    exported_messages = transcript.messages

    # Check that the messages are in the correct chronological order
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

    assert len(exported_messages) == 2
    assert exported_messages[0].created_at < exported_messages[1].created_at