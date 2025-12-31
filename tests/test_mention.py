import pytest
from unittest.mock import MagicMock

from DiscordTranscript.parse.mention import ParseMention


@pytest.fixture
def mock_guild():
    guild = MagicMock()
    guild.id = 12345
    guild.name = "Test Guild"
    return guild


@pytest.fixture
def mock_bot():
    bot = MagicMock()
    return bot


@pytest.mark.asyncio
async def test_channel_mention(mock_guild):
    channel = MagicMock()
    channel.id = 54321
    channel.name = "test-channel"
    mock_guild.get_channel.return_value = channel

    parser = ParseMention("<#54321>", mock_guild)
    await parser.channel_mention()
    assert parser.content == '<span class="mention" title="54321">#test-channel</span>'

    parser = ParseMention("&lt;#54321&gt;", mock_guild)
    await parser.channel_mention()
    assert parser.content == '<span class="mention" title="54321">#test-channel</span>'

    mock_guild.get_channel.return_value = None
    parser = ParseMention("<#12345>", mock_guild)
    await parser.channel_mention()
    assert parser.content == "#deleted-channel"


@pytest.mark.asyncio
async def test_role_mention(mock_guild):
    role = MagicMock()
    role.id = 98765
    role.name = "Test Role"
    role.color = MagicMock()
    role.color.r = 255
    role.color.g = 0
    role.color.b = 0
    mock_guild.get_role.return_value = role

    parser = ParseMention("<@&98765>", mock_guild)
    await parser.role_mention()
    assert (
        parser.content
        == '<span class="mention" style="color: #ff0000; background-color: rgba(255, 0, 0, 0.1);" title="98765">@Test Role</span>'
    )

    parser = ParseMention("&lt;@&amp;98765&gt;", mock_guild)
    await parser.role_mention()
    assert (
        parser.content
        == '<span class="mention" style="color: #ff0000; background-color: rgba(255, 0, 0, 0.1);" title="98765">@Test Role</span>'
    )

    mock_guild.get_role.return_value = None
    parser = ParseMention("<@&12345>", mock_guild)
    await parser.role_mention()
    assert parser.content == "@deleted-role"


@pytest.mark.asyncio
async def test_member_mention(mock_guild, mock_bot):
    member = MagicMock()
    member.id = 112233
    member.display_name = "TestUser"
    mock_guild.get_member.return_value = member
    mock_bot.get_user.return_value = None

    parser = ParseMention("<@112233>", mock_guild, bot=mock_bot)
    await parser.member_mention()
    assert parser.content == '<span class="mention" title="112233">@TestUser</span>'

    parser = ParseMention("&lt;@112233&gt;", mock_guild, bot=mock_bot)
    await parser.member_mention()
    assert parser.content == '<span class="mention" title="112233">@TestUser</span>'

    mock_guild.get_member.return_value = None
    parser = ParseMention("<@445566>", mock_guild, bot=mock_bot)
    await parser.member_mention()
    assert parser.content == '<span class="mention" title="445566">&lt;@445566></span>'


@pytest.mark.asyncio
async def test_time_mention(mock_guild):
    parser = ParseMention("&lt;t:1622548800:f&gt;", mock_guild, timezone="UTC")
    await parser.time_mention()
    assert "June 2021 11:59" in parser.content


@pytest.mark.asyncio
async def test_slash_command_mention(mock_guild):
    parser = ParseMention("&lt;/test command:123456789&gt;", mock_guild)
    await parser.slash_command_mention()
    assert (
        parser.content
        == '<span class="mention" title="test command">/test command</span>'
    )


@pytest.mark.asyncio
async def test_flow(mock_guild):
    channel = MagicMock()
    channel.id = 54321
    channel.name = "test-channel"
    mock_guild.get_channel.return_value = channel

    role = MagicMock()
    role.id = 98765
    role.name = "Test Role"
    role.color = MagicMock()
    role.color.r = 255
    role.color.g = 0
    role.color.b = 0
    mock_guild.get_role.return_value = role

    member = MagicMock()
    member.id = 112233
    member.display_name = "TestUser"
    mock_guild.get_member.return_value = member

    content = "Hello <@112233>, welcome to <#54321>. Please read the rules and get the <@&98765> role."
    parser = ParseMention(content, mock_guild, timezone="UTC")
    result = await parser.flow()

    assert '<span class="mention" title="112233">@TestUser</span>' in result
    assert '<span class="mention" title="54321">#test-channel</span>' in result
    assert (
        '<span class="mention" style="color: #ff0000; background-color: rgba(255, 0, 0, 0.1);" title="98765">@Test Role</span>'
        in result
    )
