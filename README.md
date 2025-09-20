# Discord HTML Transcripts (Python)

A Python library to generate HTML transcripts of Discord messages. This is a Python port of the popular [discord-html-transcripts](https://github.com/ItzDerock/discord-html-transcripts) library.

## Features

-   Generate beautiful HTML transcripts of your Discord messages.
-   Support for replies, embeds, attachments, reactions, and more.
-   Save images locally and embed them in the transcript.
-   Easy to use and customize.

## Installation

```bash
pip install discord-html-transcripts-python
```

## Usage

Here's a simple example of how to use the library:

```python
import asyncio
from discord_html_transcripts.main import generate_from_messages

async def main():
    messages = [
        {
            "author": {"name": "User1", "avatar_url": "https://via.placeholder.com/150"},
            "content": "Hello, world!",
            "timestamp": "2025-01-01 00:00:00"
        },
        {
            "author": {"name": "User2", "avatar_url": "https://via.placeholder.com/150"},
            "content": "This is a test message.",
            "timestamp": "2025-01-01 00:01:00"
        }
    ]

    channel = {"name": "test-channel", "guild_name": "Test Guild"}

    html = await generate_from_messages(messages, channel)

    with open("transcript.html", "w") as f:
        f.write(html)

if __name__ == "__main__":
    asyncio.run(main())
```

### Saving Images

You can also save images locally by setting the `save_images` option to `True`:

```python
html = await generate_from_messages(messages, channel, options={"save_images": True})
```
