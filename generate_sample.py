
import asyncio
import datetime
from unittest.mock import MagicMock
from DiscordTranscript import raw_export

# Mock objects to simulate discord.py models

class MockGuild:
    def __init__(self):
        self.id = 123456789
        self.name = "Test Server"
        self.icon = "https://cdn.discordapp.com/icons/123456789/icon.png"
        self.roles = []

    def get_member(self, id):
        return None # Return None to simulate user not in guild (or just basic handling)

class MockColor:
    def __init__(self, value):
        self.value = value
        self.r = (value >> 16) & 255
        self.g = (value >> 8) & 255
        self.b = value & 255

    def __str__(self):
        return f"#{self.value:06x}"

class MockUser:
    def __init__(self, id, name, discriminator, avatar_url, bot=False, color=None):
        self.id = id
        self.name = name
        self.discriminator = discriminator
        self.display_avatar = MagicMock()
        self.display_avatar.url = avatar_url
        self.avatar = self.display_avatar # backwards compat
        self.bot = bot
        self.color = color if color else MockColor(0xFFFFFF)
        self.display_name = name
        self.created_at = datetime.datetime.now()
        self.joined_at = datetime.datetime.now()

    def __str__(self):
        return f"{self.name}#{self.discriminator}"

class MockChannel:
    def __init__(self):
        self.id = 987654321
        self.name = "general"
        self.topic = "A place to chat"
        self.created_at = datetime.datetime.now()
        self.guild = MockGuild()
        self.history = MagicMock()
        self.type = MagicMock()
        self.type.name = "text"

class MockAttachment:
    def __init__(self, filename, url, size):
        self.filename = filename
        self.url = url
        self.size = size
        self.content_type = "image/png"
        self.height = 100
        self.width = 100
        self.is_spoiler = lambda: False

class MockEmoji:
    def __init__(self, name, url=None):
        self.name = name
        self.url = url
        self.animated = False
        self.id = 1

    def __str__(self):
        return self.name

    def __iter__(self):
        return iter(self.name)

class MockReaction:
    def __init__(self, emoji, count):
        self.emoji = emoji
        self.count = count

class MockMessage:
    def __init__(self, id, content, author, timestamp, attachments=[], embeds=[], components=[], reactions=[], reference=None, channel=None):
        self.id = id
        self.content = content
        self.author = author
        self.created_at = timestamp
        self.edited_at = None
        self.attachments = attachments
        self.embeds = embeds
        self.components = components
        self.reactions = reactions
        self.reference = reference
        self.channel = channel
        self.mentions = []
        self.channel_mentions = []
        self.role_mentions = []
        self.stickers = []
        self.type = MagicMock()
        self.type.name = "default" # "default", "reply"
        self.webhook_id = None
        self.interaction = None

        # Determine clean content
        self.clean_content = content

class MockEmbed:
    def __init__(self, title=None, description=None, color=None, fields=None, author=None, footer=None, image=None, thumbnail=None):
        self.title = title
        self.description = description
        self.color = color # int
        self.colour = MockColor(color) if color else MockColor(0x202225) # Default embed color
        self.fields = fields if fields else []
        self.author = author
        self.footer = footer
        self.image = image
        self.thumbnail = thumbnail
        self.timestamp = None
        self.url = None
        self.video = None
        self.provider = None
        self.type = 'rich'

    def to_dict(self):
        return {} # Not strictly needed for the transcript unless it uses it

class MockEmbedField:
    def __init__(self, name, value, inline):
        self.name = name
        self.value = value
        self.inline = inline

class MockEmbedProxy:
    def __init__(self, url=None, text=None, icon_url=None, name=None):
        self.url = url
        self.text = text
        self.icon_url = icon_url
        self.name = name
        self.proxy_icon_url = None

class MockButton:
    def __init__(self, label, style, url=None, emoji=None, disabled=False):
        self.label = label
        self.style = style # ButtonStyle value
        self.url = url
        self.emoji = emoji
        self.disabled = disabled
        self.type = 2 # ComponentType.button

class MockActionRow:
    def __init__(self, children):
        self.children = children
        self.type = 1 # ComponentType.action_row

class MockButtonStyle:
    primary = 1 # blurple
    secondary = 2 # grey
    success = 3 # green
    danger = 4 # red
    link = 5 # url

async def main():
    guild = MockGuild()
    channel = MockChannel()
    channel.guild = guild # Circular reference needed

    user1 = MockUser(1, "UserOne", "0001", "https://cdn.discordapp.com/embed/avatars/0.png")
    user2 = MockUser(2, "UserTwo", "0002", "https://cdn.discordapp.com/embed/avatars/1.png")

    # Message 1: Simple text
    msg1 = MockMessage(
        1001,
        "Hello world! This is a test message.",
        user1,
        datetime.datetime.now() - datetime.timedelta(minutes=5),
        channel=channel
    )

    # Message 2: Embed
    embed = MockEmbed(
        title="Test Embed",
        description="This is an embed description.",
        color=0x5865F2, # Blurple
        fields=[
            MockEmbedField("Field 1", "Value 1", True),
            MockEmbedField("Field 2", "Value 2", True),
            MockEmbedField("Field 3", "Value 3 (Not Inline)", False)
        ],
        author=MockEmbedProxy(name="Author Name", icon_url="https://cdn.discordapp.com/embed/avatars/0.png"),
        footer=MockEmbedProxy(text="Footer Text", icon_url="https://cdn.discordapp.com/embed/avatars/1.png")
    )
    msg2 = MockMessage(
        1002,
        "Here is an embed:",
        user2,
        datetime.datetime.now() - datetime.timedelta(minutes=4),
        embeds=[embed],
        channel=channel
    )

    # Message 3: Buttons
    button_blurple = MockButton("Primary", MockButtonStyle.primary)
    button_grey = MockButton("Secondary", MockButtonStyle.secondary)
    button_green = MockButton("Success", MockButtonStyle.success)
    button_red = MockButton("Danger", MockButtonStyle.danger)
    button_link = MockButton("Link", MockButtonStyle.link, url="https://discord.com")

    action_row = MockActionRow([button_blurple, button_grey, button_green, button_red, button_link])

    msg3 = MockMessage(
        1003,
        "Here are some buttons:",
        user1,
        datetime.datetime.now() - datetime.timedelta(minutes=3),
        components=[action_row],
        channel=channel
    )

    # Message 4: Reaction
    reaction = MockReaction(MockEmoji("👍"), 5)
    msg4 = MockMessage(
        1004,
        "React to this!",
        user2,
        datetime.datetime.now() - datetime.timedelta(minutes=2),
        reactions=[reaction],
        channel=channel
    )

    messages = [msg1, msg2, msg3, msg4]

    html = await raw_export(channel, messages, guild=guild)

    with open("test_render.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Generated test_render.html")

if __name__ == "__main__":
    asyncio.run(main())
