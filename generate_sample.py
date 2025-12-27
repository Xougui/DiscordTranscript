
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
        self.public_flags = MagicMock()
        self.public_flags.verified_bot = False

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
        self.proxy_url = url
        self.size = size
        self.content_type = "image/png"
        self.height = 100
        self.width = 100
        self.is_spoiler = lambda: False

class MockSticker:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.format = "png"

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
    def __init__(self, id, content, author, timestamp, attachments=[], embeds=[], components=[], reactions=[], reference=None, channel=None, stickers=[]):
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
        self.stickers = stickers
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
        self.proxy_url = url

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

class MockSelectOption:
    def __init__(self, label, value, description=None, emoji=None, default=False):
        self.label = label
        self.value = value
        self.description = description
        self.emoji = emoji
        self.default = default

class MockSelectMenu:
    def __init__(self, custom_id, options, placeholder=None, min_values=1, max_values=1, disabled=False):
        self.custom_id = custom_id
        self.options = options
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.disabled = disabled
        self.type = 3 # ComponentType.string_select

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

    user1 = MockUser(1, "Alice", "0001", "https://cdn.discordapp.com/embed/avatars/0.png", color=MockColor(0xFF0000))
    user2 = MockUser(2, "Bob", "0002", "https://cdn.discordapp.com/embed/avatars/1.png", color=MockColor(0x00FF00))
    bot_user = MockUser(3, "HelperBot", "9999", "https://cdn.discordapp.com/embed/avatars/2.png", bot=True, color=MockColor(0x5865F2))

    base_time = datetime.datetime.now() - datetime.timedelta(hours=1)

    # Message 1: Simple text
    msg1 = MockMessage(
        1001,
        "Salut tout le monde ! Bienvenue sur le canal de test.",
        user1,
        base_time,
        channel=channel
    )

    # Message 2: Reply
    msg2 = MockMessage(
        1002,
        "Salut Alice ! Content d'être là.",
        user2,
        base_time + datetime.timedelta(minutes=1),
        channel=channel,
        reference=MagicMock(resolved=msg1, message_id=msg1.id, guild_id=guild.id, channel_id=channel.id)
    )
    msg2.type.name = "reply"

    # Message 3: Markdown Showcase
    markdown_content = (
        "Voici un peu de **gras**, de l'*italique*, et du __souligné__.\n"
        "On peut aussi faire du `code en ligne` ou des blocs :\n"
        "```python\nprint('Hello World')\n```\n"
        "> Et une citation !"
    )
    msg3 = MockMessage(
        1003,
        markdown_content,
        user1,
        base_time + datetime.timedelta(minutes=5),
        channel=channel
    )

    # Message 4: Attachment
    attachment = MockAttachment("image_test.png", "https://via.placeholder.com/150", 1024)
    msg4 = MockMessage(
        1004,
        "Regardez cette image :",
        user2,
        base_time + datetime.timedelta(minutes=10),
        attachments=[attachment],
        channel=channel
    )

    # Message 5: Complex Embed
    embed = MockEmbed(
        title="Rapport de Statut",
        description="Ceci est un exemple d'embed complexe.",
        color=0x5865F2, # Blurple
        fields=[
            MockEmbedField("Statut", "En ligne", True),
            MockEmbedField("Latence", "23ms", True),
            MockEmbedField("Détails", "Tout fonctionne correctement.", False)
        ],
        author=MockEmbedProxy(name="Système", icon_url="https://cdn.discordapp.com/embed/avatars/0.png"),
        footer=MockEmbedProxy(text="Mis à jour à l'instant", icon_url="https://cdn.discordapp.com/embed/avatars/1.png"),
        thumbnail=MockEmbedProxy(url="https://cdn.discordapp.com/embed/avatars/2.png"),
        image=MockEmbedProxy(url="https://via.placeholder.com/400x100")
    )
    msg5 = MockMessage(
        1005,
        "",
        bot_user,
        base_time + datetime.timedelta(minutes=15),
        embeds=[embed],
        channel=channel
    )

    # Message 6: Components (Buttons)
    button_blurple = MockButton("Confirmer", MockButtonStyle.primary, emoji=MockEmoji("✅"))
    button_red = MockButton("Annuler", MockButtonStyle.danger, emoji=MockEmoji("✖️"))
    button_link = MockButton("Documentation", MockButtonStyle.link, url="https://discord.com")

    action_row_buttons = MockActionRow([button_blurple, button_red, button_link])

    msg6 = MockMessage(
        1006,
        "Veuillez faire un choix :",
        bot_user,
        base_time + datetime.timedelta(minutes=20),
        components=[action_row_buttons],
        channel=channel
    )

    # Message 7: Components (Select Menu)
    select_options = [
        MockSelectOption("Option 1", "1", "Description 1", MockEmoji("1️⃣")),
        MockSelectOption("Option 2", "2", "Description 2", MockEmoji("2️⃣"), default=True),
        MockSelectOption("Option 3", "3", "Description 3", MockEmoji("3️⃣"))
    ]
    select_menu = MockSelectMenu("select_1", select_options, placeholder="Choisissez une option...")
    action_row_select = MockActionRow([select_menu])

    msg7 = MockMessage(
        1007,
        "Sélectionnez un élément dans la liste :",
        bot_user,
        base_time + datetime.timedelta(minutes=21),
        components=[action_row_select],
        channel=channel
    )

    # Message 8: Sticker
    sticker = MockSticker("Wumpus Wave", "https://cdn.discordapp.com/stickers/1234567890.png")
    msg8 = MockMessage(
        1008,
        "",
        user1,
        base_time + datetime.timedelta(minutes=25),
        stickers=[sticker],
        channel=channel
    )

    # Message 9: Reactions
    reaction1 = MockReaction(MockEmoji("👍"), 5)
    reaction2 = MockReaction(MockEmoji("🔥"), 2)
    msg9 = MockMessage(
        1009,
        "Ce message est très populaire !",
        user2,
        base_time + datetime.timedelta(minutes=30),
        reactions=[reaction1, reaction2],
        channel=channel
    )

    # Message 11: Future message (Alice)
    msg11 = MockMessage(
        1011,
        "Je viens du futur !",
        user1,
        base_time + datetime.timedelta(minutes=35),
        channel=channel
    )

    # Message 10: Reply to future message (Bob)
    msg10 = MockMessage(
        1010,
        "Attends, tu as envoyé ça dans le futur ?",
        user2,
        base_time + datetime.timedelta(minutes=40),
        channel=channel,
        reference=MagicMock(resolved=msg11, message_id=msg11.id, guild_id=guild.id, channel_id=channel.id)
    )
    msg10.type.name = "reply"

    messages = [msg10, msg11, msg9, msg8, msg7, msg6, msg5, msg4, msg3, msg2, msg1]

    html = await raw_export(channel, messages, guild=guild)

    with open("test_render.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Generated test_render.html")

if __name__ == "__main__":
    asyncio.run(main())
