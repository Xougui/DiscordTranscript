import os
import discord
from jinja2 import Environment, FileSystemLoader
import base64
import requests
import markdown

# Load the template
templates_path = os.path.join(os.path.dirname(__file__), 'templates')
env = Environment(loader=FileSystemLoader(templates_path))

# markdown filter
def markdown_filter(text):
    return markdown.markdown(text, extensions=['pymdownx.magiclink', 'pymdownx.emoji'])

env.filters['markdown'] = markdown_filter


async def create_transcript(channel: discord.TextChannel, options: dict = None):
    """
    Creates a transcript from a discord channel.
    """
    if options is None:
        options = {}

    messages = await channel.history(limit=options.get("limit", None)).flatten()
    return await generate_from_messages(messages, channel, options)

async def generate_from_messages(messages, channel, options: dict = None):
    """
    Generates a transcript from a list of messages.
    """
    if options is None:
        options = {}

    if options.get('save_images'):
        for message in messages:
            if message.attachments:
                for attachment in message.attachments:
                    if attachment.content_type and attachment.content_type.startswith('image/'):
                        try:
                            response = requests.get(attachment.url)
                            response.raise_for_status()
                            encoded_image = base64.b64encode(response.content).decode('utf-8')
                            attachment.url = f"data:{attachment.content_type};base64,{encoded_image}"
                        except requests.exceptions.RequestException:
                            pass
            if message.embeds:
                for embed in message.embeds:
                    if embed.image and embed.image.url:
                        try:
                            response = requests.get(embed.image.url)
                            response.raise_for_status()
                            encoded_image = base64.b64encode(response.content).decode('utf-8')
                            embed.image.url = f"data:image/png;base64,{encoded_image}"
                        except requests.exceptions.RequestException:
                            pass

    template = env.get_template('template.html')
    return template.render(messages=messages, channel=channel)
