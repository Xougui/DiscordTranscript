import asyncio
import html
import sys
import os

# Add current directory to sys.path
sys.path.append(os.getcwd())

from DiscordTranscript.parse.markdown import ParseMarkdown

content = """
```py
print('Hello')
```
"""
# Emulate message.py logic:
escaped_content = html.escape(content).replace("&#96;", "`")
print(f"Input to ParseMarkdown:\n{escaped_content}")

pm = ParseMarkdown(escaped_content)

async def run():
    res = await pm.standard_message_flow()
    print(f"Output:\n{res}")

asyncio.run(run())
