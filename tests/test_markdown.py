import pytest
from DiscordTranscript.parse.markdown import ParseMarkdown


@pytest.mark.asyncio
async def test_bold_markdown():
    parser = ParseMarkdown("**hello world**")
    await parser.standard_message_flow()
    assert parser.content.strip() == "<strong>hello world</strong>"


@pytest.mark.asyncio
async def test_underline_markdown():
    parser = ParseMarkdown("__hello world__")
    await parser.standard_message_flow()
    assert (
        parser.content.strip()
        == '<span class="markdown-underline">hello world</span>'
    )


@pytest.mark.asyncio
async def test_italic_markdown():
    parser = ParseMarkdown("*hello world*")
    await parser.standard_message_flow()
    assert parser.content.strip() == "<em><span>hello world</span></em>"


@pytest.mark.asyncio
async def test_italic_underscore_markdown():
    parser = ParseMarkdown("_hello world_")
    await parser.standard_message_flow()
    assert parser.content.strip() == "<em><span>hello world</span></em>"


@pytest.mark.asyncio
async def test_strike_through_markdown():
    parser = ParseMarkdown("~~hello world~~")
    await parser.standard_message_flow()
    assert (
        parser.content.strip()
        == '<span class="markdown-strikethrough">hello world</span>'
    )


@pytest.mark.asyncio
async def test_h1_markdown():
    parser = ParseMarkdown("# hello world")
    await parser.standard_message_flow()
    assert parser.content.strip() == "<h1>hello world</h1>"


@pytest.mark.asyncio
async def test_h2_markdown():
    parser = ParseMarkdown("## hello world")
    await parser.standard_message_flow()
    assert parser.content.strip() == "<h2>hello world</h2>"


@pytest.mark.asyncio
async def test_h3_markdown():
    parser = ParseMarkdown("### hello world")
    await parser.standard_message_flow()
    assert parser.content.strip() == "<h3>hello world</h3>"


@pytest.mark.asyncio
async def test_spoiler_markdown():
    parser = ParseMarkdown("||hello world||")
    await parser.standard_message_flow()
    assert (
        parser.content.strip()
        == '<span class="spoiler spoiler--hidden" onclick="showSpoiler(event, this)"> <span class="spoiler-text">hello world</span></span>'
    )


@pytest.mark.asyncio
async def test_quote_markdown():
    parser = ParseMarkdown("&gt; hello world")
    await parser.standard_message_flow()
    assert parser.content.strip() == '<div class="quote">hello world</div>'


@pytest.mark.asyncio
async def test_code_block_markdown():
    parser = ParseMarkdown("`hello world`")
    await parser.standard_message_flow()
    assert "hello world" in parser.content


@pytest.mark.asyncio
async def test_multiline_code_block_markdown():
    parser = ParseMarkdown("```\nhello world\n```")
    await parser.standard_message_flow()
    assert "hello world" in parser.content


@pytest.mark.asyncio
async def test_link_markdown():
    parser = ParseMarkdown("[google](https://google.com)")
    parser.parse_embed_markdown()
    assert parser.content == '<a href="https://google.com">google</a>'


@pytest.mark.asyncio
async def test_https_link():
    parser = ParseMarkdown("https://google.com")
    await parser.standard_message_flow()
    assert (
        parser.content.strip() == '<a href="https://google.com">https://google.com</a>'
    )


@pytest.mark.asyncio
async def test_emoji():
    parser = ParseMarkdown(":joy:")
    await parser.special_emoji_flow()
    assert ":joy:" in parser.content


@pytest.mark.asyncio
async def test_custom_emoji():
    parser = ParseMarkdown("<:custom:12345>")
    await parser.parse_emoji()
    assert (
        '<img class="emoji emoji--small" src="https://cdn.discordapp.com/emojis/12345.png" alt="Emoji">'
        in parser.content
    )
