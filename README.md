<div align="center">
    <h2>Py-Discord-HTML-Transcripts</h2>
</div>

---
# Requirements
`discord.py` v2.4.0 or later

---
## Installation

To install the library to your virtual environment, for bot usage, run the command:
```sh 
pip install py-discord-html-transcripts
```

---
## Usage

There are currently 3 methods (functions) to `chat-exporter` which you can use to export your chat.<br/>
_Expand the blocks below to learn the functions, arguments and usages._
<details><summary><b>Basic Usage</b></summary>

`.quick_export()` is the simplest way of using chat-exporter.

Using the _quick_export_ function will gather the history of the channel you give, build the transcript then post the file and embed directly to the channel - returning a message object gathered from the message it posted.

This is mostly seen as a demo function, as opposed to a command you should actually use. 

**Required Argument(s):**<br/>
`channel`: `discord.TextChannel` object, whether `ctx.channel` or any channel you gather.

**Optional Argument(s):**<br/>
`bot`: `commands.Bot` object to gather members who are no longer in your guild.

**Return Argument:**<br/>
`discord.Message`: The message _quick_export_ will send, containing the embed and exported chat file.

**Example:**
```python
import discord
import chat_exporter
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

...

@bot.command()
async def save(ctx: commands.Context):
    await chat_exporter.quick_export(ctx.channel)

...
```

</details>

<details><summary><b>Customisable Usage</b></summary>

`.export()` is the most efficient and flexible method to export a chat using chat-exporter.

Using the _export_ function will generate a transcript using the channel you pass in, along with using any of the custom kwargs passed in to set limits, timezone, 24h formats and more (listed below).

This would be the main function to use within chat-exporter.

**Required Argument(s):**<br/>
`channel`: `discord.TextChannel` object, whether `ctx.channel` or any channel you gather.

**Optional Argument(s):**<br/>
`limit`: Integer value to set the limit (amount of messages) the chat exporter gathers when grabbing the history (default=unlimited).<br/>
`tz_info`: String value of a [TZ Database name](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List) to set a custom timezone for the exported messages (default=UTC)<br/>
`guild`: `discord.Guild` object which can be passed in to solve bugs for certain forks<br/>
`military_time`: Boolean value to set a 24h format for times within your exported chat (default=False | 12h format)<br/>
`fancy_times`: Boolean value which toggles the 'fancy times' (Today|Yesterday|Day)<br/>
`before`: `datetime.datetime` object which allows to gather messages from before a certain date
`after`: `datetime.datetime` object which allows to gather messages from after a certain date
`bot`: `commands.Bot` object to gather members who are no longer in your guild.

**Return Argument:**<br/>
`transcript`: The HTML build-up for you to construct the HTML File with Discord.

**Example:**
```python
import io

...

@bot.command()
async def save(ctx: commands.Context, limit: int = 100, tz_info: str = "UTC", military_time: bool = True):
    transcript = await chat_exporter.export(
        ctx.channel,
        limit=limit,
        tz_info=tz_info,
        military_time=military_time,
        bot=bot,
    )

    if transcript is None:
        return

    transcript_file = discord.File(
        io.BytesIO(transcript.encode()),
        filename=f"transcript-{ctx.channel.name}.html",
    )

    await ctx.send(file=transcript_file)
```
</details>
<details><summary><b>Raw Usage</b></summary>

`.raw_export()` is for the crazy people who like to do their own thing when using chat-exporter.

Using the _raw_export_ function will generate a transcript using the list of messages you pass in, along with using any of the custom kwargs passed in to set limits, timezone, 24h formats and more (listed below).

This would be for people who want to filter what content to export.

**Required Argument(s):**<br/>
`channel`: `discord.TextChannel` object, whether `ctx.channel` or any channel you gather (this is just for padding the header).<br/>
`messages`: A list of Message objects which you wish to export to an HTML file.

**Optional Argument(s):**<br/>
`tz_info`: String value of a [TZ Database name](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List) to set a custom timezone for the exported messages (default=UTC)<br/>
`military_time`: Boolean value to set a 24h format for times within your exported chat (default=False | 12h format)<br/>
`fancy_times`: Boolean value which toggles the 'fancy times' (Today|Yesterday|Day)<br/>
`bot`: `commands.Bot` object to gather members who are no longer in your guild.

**Return Argument:**<br/>
`transcript`: The HTML build-up for you to construct the HTML File with Discord.

**Example:**
```python
import io

...

@bot.command()
async def purge(ctx: commands.Context, tz_info: str, military_time: bool):
    deleted_messages = await ctx.channel.purge()

    transcript = await chat_exporter.raw_export(
        ctx.channel,
        messages=deleted_messages,
        tz_info=tz_info,
        military_time=military_time,
        bot=bot,
    )

    if transcript is None:
        return

    transcript_file = discord.File(
        io.BytesIO(transcript.encode()),
        filename=f"transcript-{ctx.channel.name}.html",
    )

    await ctx.send(file=transcript_file)
```
</details>

<p align="right">(<a href="#top">back to top</a>)</p>

---
## Screenshots

<details><summary><b>General</b></summary>
<ol>
    <details><summary>Discord</summary>
    <img src="https://raw.githubusercontent.com/FroostySnoowman/py-discord-html-transcripts/master/.screenshots/channel.png">
    </details>
    <details><summary>Chat-Exporter</summary>
    <img src="https://raw.githubusercontent.com/FroostySnoowman/py-discord-html-transcripts/master/.screenshots/export.png">
    </details>
</ol>
</details>
<p align="right">(<a href="#top">back to top</a>)</p>