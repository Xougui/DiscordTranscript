from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import DiscordTranscript.chat_exporter as chat_exporter


@pytest.fixture
def mock_channel():
    channel = AsyncMock()
    channel.name = "test-channel"
    channel.guild = MagicMock()
    return channel


@pytest.fixture
def mock_bot():
    return MagicMock()


@pytest.fixture
def mock_transcript():
    transcript = MagicMock()
    transcript.html = "<html><body>Test Transcript</body></html>"
    return transcript


@pytest.mark.asyncio
@patch("DiscordTranscript.chat_exporter.Transcript")
async def test_quick_export(
    MockTranscript, mock_channel, mock_bot, mock_transcript
) -> None:
    mock_transcript_instance = mock_transcript
    mock_transcript_instance.export = AsyncMock(return_value=mock_transcript_instance)
    MockTranscript.return_value = mock_transcript_instance

    await chat_exporter.quick_export(mock_channel, bot=mock_bot)

    MockTranscript.assert_called_once()
    mock_channel.send.assert_called_once()


@pytest.mark.asyncio
@patch("DiscordTranscript.chat_exporter.Transcript")
async def test_export(MockTranscript, mock_channel, mock_bot, mock_transcript) -> None:
    mock_transcript_instance = mock_transcript
    mock_transcript_instance.export = AsyncMock(return_value=mock_transcript_instance)
    MockTranscript.return_value = mock_transcript_instance

    html = await chat_exporter.export(mock_channel, bot=mock_bot)

    MockTranscript.assert_called_once()
    assert html == mock_transcript.html


@pytest.mark.asyncio
@patch("DiscordTranscript.chat_exporter.Transcript")
async def test_raw_export(
    MockTranscript, mock_channel, mock_bot, mock_transcript
) -> None:
    mock_transcript_instance = mock_transcript
    mock_transcript_instance.export = AsyncMock(return_value=mock_transcript_instance)
    MockTranscript.return_value = mock_transcript_instance
    messages = [MagicMock()]

    html = await chat_exporter.raw_export(mock_channel, messages=messages, bot=mock_bot)

    MockTranscript.assert_called_once()
    assert html == mock_transcript.html
