import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from DiscordTranscript import (
    DEFAULT_CUSTOM_COLORS,
    export,
    generate_custom_colors_file,
    raw_export,
)
from DiscordTranscript.construct.custom_colors import parse_custom_colors_file
from DiscordTranscript.construct.transcript import Transcript


@pytest.fixture
def mock_channel():
    channel = AsyncMock()
    channel.name = "test-channel"
    channel.id = 123456789
    channel.topic = ""
    channel.guild = MagicMock()
    channel.guild.id = 987654321
    channel.guild.name = "test-guild"
    channel.created_at = datetime.datetime.now()
    channel.guild.icon = ""
    channel.guild.timezone = "UTC"
    return channel


def create_mock_message(content, created_at):
    message = MagicMock()
    message.content = content
    message.created_at = created_at
    message.edited_at = None
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


def test_parse_valid_custom_colors_file(tmp_path: Path):
    colors_file = tmp_path / "theme.txt"
    colors_file.write_text(
        """# Custom Theme Header
// Comment line
background-primary: #112233
--background-secondary: #445566;
text_normal: #fafafa
/* Multi line style comment */

--discord-blurple: rgb(88, 101, 242)
""",
        encoding="utf-8",
    )

    css = parse_custom_colors_file(colors_file)
    assert "--background-primary: #112233;" in css
    assert "--background-secondary: #445566;" in css
    assert "--text-normal: #fafafa;" in css
    assert "--discord-blurple: rgb(88, 101, 242);" in css


def test_parse_non_existent_file(tmp_path: Path):
    non_existent = tmp_path / "does_not_exist.txt"
    with pytest.raises(FileNotFoundError):
        parse_custom_colors_file(non_existent)


def test_parse_invalid_syntax_missing_colon(tmp_path: Path):
    colors_file = tmp_path / "invalid.txt"
    colors_file.write_text("background-primary #123456\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Expected 'key: value'"):
        parse_custom_colors_file(colors_file)


def test_parse_empty_key_or_value(tmp_path: Path):
    colors_file = tmp_path / "empty_key.txt"
    colors_file.write_text(": #123456\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid key"):
        parse_custom_colors_file(colors_file)

    colors_file_val = tmp_path / "empty_val.txt"
    colors_file_val.write_text("background-primary:\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid value"):
        parse_custom_colors_file(colors_file_val)


@pytest.mark.asyncio
async def test_transcript_with_custom_colors(mock_channel, tmp_path: Path):
    colors_file = tmp_path / "colors.txt"
    colors_file.write_text(
        "background-primary: #ff007f\n--text-normal: #00ff00;\n",
        encoding="utf-8",
    )

    msg = create_mock_message("hello", datetime.datetime(2023, 1, 1, 12, 0, 0))

    async def mock_history_generator():
        yield msg

    mock_channel.history = MagicMock(return_value=mock_history_generator())

    transcript = Transcript(
        channel=mock_channel,
        limit=1,
        messages=None,
        pytz_timezone="UTC",
        military_time=False,
        fancy_times=True,
        before=None,
        after=None,
        bot=None,
        attachment_handler=None,
        custom_colors_file=colors_file,
    )
    result = await transcript.export()
    assert "--background-primary: #ff007f;" in result.html
    assert "--text-normal: #00ff00;" in result.html


@pytest.mark.asyncio
async def test_export_and_raw_export_with_custom_colors(mock_channel, tmp_path: Path):
    colors_file = tmp_path / "colors.txt"
    colors_file.write_text(
        "background-primary: #010203\n",
        encoding="utf-8",
    )

    msg = create_mock_message("world", datetime.datetime(2023, 1, 1, 12, 0, 0))

    async def mock_history_generator():
        yield msg

    mock_channel.history = MagicMock(return_value=mock_history_generator())

    html_export = await export(mock_channel, limit=1, custom_colors_file=colors_file)
    assert "--background-primary: #010203;" in html_export

    html_raw = await raw_export(mock_channel, [msg], custom_colors_file=colors_file)
    assert "--background-primary: #010203;" in html_raw


def test_default_custom_colors_dict():
    assert isinstance(DEFAULT_CUSTOM_COLORS, dict)
    assert "background-primary" in DEFAULT_CUSTOM_COLORS
    assert "discord-blurple" in DEFAULT_CUSTOM_COLORS
    assert DEFAULT_CUSTOM_COLORS["background-primary"] == "#313338"


def test_generate_custom_colors_file(tmp_path: Path):
    target = tmp_path / "subdir" / "my_custom_theme.txt"
    created = generate_custom_colors_file(target)
    assert created.exists()
    assert created.is_file()

    # Verify that the generated template is directly parsable
    css = parse_custom_colors_file(created)
    assert "--background-primary: #313338;" in css
    assert "--discord-blurple: #5865F2;" in css

    # Test overwrite protection
    with pytest.raises(FileExistsError):
        generate_custom_colors_file(target, overwrite=False)

    # Test overwrite success
    target.write_text("dummy", encoding="utf-8")
    generate_custom_colors_file(target, overwrite=True)
    assert "dummy" not in target.read_text(encoding="utf-8")
    assert "background-primary: #313338" in target.read_text(encoding="utf-8")

