import os
import asyncio
import datetime
import re
from unittest.mock import MagicMock
from DiscordTranscript import raw_export
import discord

# Mock objects to simulate discord.py models


class MockAsset:
    def __init__(self, url):
        self.url = url

    def __str__(self):
        return self.url


class MockGuild:
    def __init__(self):
        self.id = 123456789
        self.name = "Serveur de Démonstration"
        self.icon = "https://images-ext-1.discordapp.net/external/eWd-a9CcVDoj8a-UH3tcpShBjAHE9pcuAhI7lWv_u6o/%3Fsize%3D1024/https/cdn.discordapp.com/icons/1449148933732306976/c15c158e4c693ad4294f35f8253610b6.png?format=webp&quality=lossless&width=921&height=921"
        self.roles = [
            MockRole(999, "Admin", MockColor(0xE91E63)),
            MockRole(888, "Modérateur", MockColor(0x9B59B6)),
        ]

    def get_role(self, id):
        for role in self.roles:
            if role.id == id:
                return role
        return None

    def get_member(self, id):
        return None

    def fetch_member(self, id):
        return None


class MockColor:
    def __init__(self, value):
        self.value = value
        self.r = (value >> 16) & 255
        self.g = (value >> 8) & 255
        self.b = value & 255

    def __str__(self):
        return f"#{self.value:06x}"


class MockRole:
    def __init__(self, id, name, color=None):
        self.id = id
        self.name = name
        self.color = color if color else MockColor(0xFFFFFF)


class MockUser:
    def __init__(self, id, name, discriminator, avatar_url, bot=False, color=None):
        self.id = id
        self.name = name
        self.discriminator = discriminator
        self.display_avatar = MockAsset(avatar_url)
        self.avatar = self.display_avatar
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
        self.name = "général"
        self.topic = "Un salon pour discuter de tout et de rien"
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
        self.id = 12345

    def fetch(self):
        pass


class MockEmoji:
    def __init__(self, name, id=None, animated=False):
        self.name = name
        self.id = id
        self.animated = animated
        ext = "gif" if animated else "png"
        emoji_id = id if id else 1380533490474549250
        self.url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}"

    def __str__(self):
        if self.id:
            anim = "a" if self.animated else ""
            return f"<{anim}:{self.name}:{self.id}>"
        return self.name


class MockReaction:
    def __init__(self, emoji, count):
        self.emoji = emoji
        self.count = count


class MockMessage:
    def __init__(
        self,
        id,
        content,
        author,
        timestamp,
        attachments=None,
        embeds=None,
        components=None,
        reactions=None,
        reference=None,
        channel=None,
        stickers=None,
        interaction_metadata=None,
        type_name="default",
    ):
        self.id = id
        self.content = content
        self.author = author
        self.created_at = timestamp
        self.edited_at = None
        self.attachments = attachments or []
        self.embeds = embeds or []
        self.components = components or []
        self.reactions = reactions or []
        self.reference = reference
        self.channel = channel
        self.mentions = []
        self.channel_mentions = []
        self.role_mentions = []
        self.stickers = stickers or []
        self.type = MagicMock()
        self.type.name = type_name
        self.webhook_id = None
        self.interaction = None
        self.interaction_metadata = interaction_metadata
        self.clean_content = content


class MockEmbed:
    def __init__(
        self,
        title=None,
        description=None,
        color=None,
        fields=None,
        author=None,
        footer=None,
        image=None,
        thumbnail=None,
        timestamp=None,
    ):
        self.title = title
        self.description = description
        self.color = color
        self.colour = MockColor(color) if color else MockColor(0x202225)
        self.fields = fields if fields else []
        self.author = author
        self.footer = footer
        self.image = image
        self.thumbnail = thumbnail
        self.timestamp = timestamp
        self.url = None
        self.video = None
        self.provider = None
        self.type = "rich"


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


# Inherit from discord.Button/SelectMenu so isinstance checks pass
class MockButton(discord.Button):
    def __init__(self, label, style, url=None, emoji=None, disabled=False):
        # We don't call super().__init__ because it might require arguments or state we don't want to manage
        self.label = label
        self.style = style
        self.url = url
        self.emoji = emoji
        self.disabled = disabled
        # self.type is a property in discord.Button returning ComponentType.button
        self._underlying = MagicMock()  # Just in case


class MockActionRow:
    def __init__(self, children):
        self.children = children
        self.type = discord.ComponentType.action_row


class MockSelectOption:
    def __init__(self, label, value, description=None, emoji=None, default=False):
        self.label = label
        self.value = value
        self.description = description
        self.emoji = emoji
        self.default = default


class MockSelectMenu(discord.SelectMenu):
    def __init__(
        self,
        custom_id,
        options,
        placeholder=None,
        min_values=1,
        max_values=1,
        disabled=False,
    ):
        self.custom_id = custom_id
        self.options = options
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.disabled = disabled
        # self.type is a property
        self._underlying = MagicMock()


class MockButtonStyle:
    primary = discord.ButtonStyle.primary
    secondary = discord.ButtonStyle.secondary
    success = discord.ButtonStyle.success
    danger = discord.ButtonStyle.danger
    link = discord.ButtonStyle.link


class MockInteractionMetadata:
    def __init__(self, user, name=None):
        self.user = user
        self.name = name
        self.id = 1234567890


async def main():
    guild = MockGuild()
    channel = MockChannel()
    channel.guild = guild

    # Users with the provided images
    user1 = MockUser(
        1,
        "Alice 🧪",
        "1378",
        "https://preview.redd.it/the-new-discord-default-profile-pictures-v0-dd62486xej7f1.png?width=1024&format=png&auto=webp&s=834060ca1b6be81c4d32adfbfc7dcdbb7018cf32",
        color=MockColor(0xFF0000),
    )
    user2 = MockUser(
        2,
        "Bob",
        "8462",
        "https://preview.redd.it/the-new-discord-default-profile-pictures-v0-4zgagzeyej7f1.png?width=1024&format=png&auto=webp&s=36a85f787f4826665e26be46c3b509281551a043",
        color=MockColor(0x00FF00),
    )
    bot_user = MockUser(
        3,
        "Lyxios",
        "4628",
        "https://lyxios.xouxou-hosting.fr/images/PDP_Lyxios.webp",
        bot=True,
        color=MockColor(0x5865F2),
    )

    base_time = datetime.datetime.now() - datetime.timedelta(hours=1)

    # Message 1: Simple text
    msg1 = MockMessage(
        1001,
        "Salut tout le monde ! Bienvenue sur le canal de test. Voici un exemple complet de transcript.",
        user1,
        base_time + datetime.timedelta(seconds=30),
        channel=channel,
    )

    # Message 2: Reply
    msg2 = MockMessage(
        1002,
        "Salut Alice ! J'adore ta photo de profil.",
        user2,
        base_time + datetime.timedelta(minutes=1),
        channel=channel,
        reference=MagicMock(
            resolved=msg1, message_id=msg1.id, guild_id=guild.id, channel_id=channel.id
        ),
    )
    msg2.type.name = "reply"

    # Message 3: Markdown and Custom Emojis
    custom_emoji_str = "<:mmmh_yeah:1448700603319451731>"
    markdown_content = (
        f"Voici un peu de **gras**, de l'*italique*, et du __souligné__.\n"
        f"Et voici un emoji personnalisé : {custom_emoji_str}\n"
        "```python\nprint('Hello World')\n```"
    )
    msg3 = MockMessage(
        1003,
        markdown_content,
        user1,
        base_time + datetime.timedelta(minutes=5),
        channel=channel,
    )

    # Message 4: Attachment (Image)
    attachment = MockAttachment(
        "photo_vacances.png",
        "https://lyxios.xouxou-hosting.fr/images/black_white.png",
        1024,
    )
    msg4 = MockMessage(
        1004,
        "Regardez cette image en pièce jointe :",
        user2,
        base_time + datetime.timedelta(minutes=10),
        attachments=[attachment],
        channel=channel,
    )

    # Message 5: Complex Embed
    embed = MockEmbed(
        title="Rapport de Statut",
        description="Ceci est un exemple d'embed riche avec des champs.",
        color=0x5865F2,
        fields=[
            MockEmbedField("Statut", "En ligne", True),
            MockEmbedField("Latence", "23ms", True),
            MockEmbedField("Version", "1.0.0", False),
        ],
        author=MockEmbedProxy(
            name="Système",
            icon_url="https://lyxios.xouxou-hosting.fr/images/PDP_Lyxios.webp",
            url="https://github.com/Xougui/DiscordTranscript",  # Link Added
        ),
        footer=MockEmbedProxy(
            text="Généré automatiquement",
            icon_url="https://lyxios.xouxou-hosting.fr/images/white_black.png",
        ),
        thumbnail=MockEmbedProxy(
            url="https://lyxios.xouxou-hosting.fr/images/black_white.png"
        ),
        image=MockEmbedProxy(
            url="https://lyxios.xouxou-hosting.fr/images/white_black.png"
        ),
    )
    msg5 = MockMessage(
        1005,
        "",
        bot_user,
        base_time + datetime.timedelta(minutes=15),
        embeds=[embed],
        channel=channel,
    )

    # Message 6: Components (Buttons)
    custom_emoji = MockEmoji("custom_check", id=1350435235015426130, animated=True)
    button_primary = MockButton(
        "Confirmer", MockButtonStyle.primary, emoji=custom_emoji
    )
    button_secondary = MockButton(
        "Options", MockButtonStyle.secondary, emoji=MockEmoji("⚙️")
    )
    button_danger = MockButton(
        "Supprimer", MockButtonStyle.danger, emoji=MockEmoji("🗑️")
    )
    button_link = MockButton(
        "Site Web", MockButtonStyle.link, url="https://discord.com"
    )

    action_row_buttons = MockActionRow(
        [button_primary, button_secondary, button_danger, button_link]
    )

    msg6 = MockMessage(
        1006,
        "Veuillez choisir une action :",
        bot_user,
        base_time + datetime.timedelta(minutes=20),
        components=[action_row_buttons],
        channel=channel,
    )

    # Message 7: Components (Select Menu)
    select_options = [
        MockSelectOption(
            "Option 1", "1", "Ceci est la première option", MockEmoji("1️⃣")
        ),
        MockSelectOption(
            "Option 2",
            "2",
            "Celle-ci est sélectionnée par défaut",
            MockEmoji("2️⃣"),
            default=True,
        ),
        MockSelectOption(
            "Option 3",
            "3",
            "Une autre option sympa",
            MockEmoji("rocket", id=1380533490474549250),
        ),
    ]
    select_menu = MockSelectMenu(
        "select_1", select_options, placeholder="Faites votre choix..."
    )
    action_row_select = MockActionRow([select_menu])

    msg7 = MockMessage(
        1007,
        "Quel est votre chiffre préféré ?",
        bot_user,
        base_time + datetime.timedelta(minutes=21),
        components=[action_row_select],
        channel=channel,
    )

    # Message 8: Sticker
    sticker = MockSticker(
        "Cool Sticker", "https://lyxios.xouxou-hosting.fr/images/PDP_Lyxios.webp"
    )
    msg8 = MockMessage(
        1008,
        "",
        user1,
        base_time + datetime.timedelta(minutes=25),
        stickers=[sticker],
        channel=channel,
    )

    # Message 9: Reactions
    # Important: Pass string for unicode emoji, MockEmoji for custom (or string for custom if formatted properly, but MockEmoji handles the id)
    reaction1 = MockReaction("👍", 10)  # Pass string directly
    reaction2 = MockReaction(
        MockEmoji("panda_fire", id=1323626699870441502, animated=True), 4
    )
    msg9 = MockMessage(
        1009,
        "Merci pour votre participation !",
        user2,
        base_time + datetime.timedelta(minutes=30),
        reactions=[reaction1, reaction2],
        channel=channel,
    )

    # Message 10: Role Mention
    msg10 = MockMessage(
        1010,
        "Voici une mention de rôle : <@&999>",
        user1,
        base_time + datetime.timedelta(minutes=35),
        channel=channel,
    )

    # Message 11: Slash Command
    interaction_meta = MockInteractionMetadata(user1, "exemple")
    msg11 = MockMessage(
        1011,
        "",
        bot_user,
        base_time + datetime.timedelta(minutes=40),
        channel=channel,
        interaction_metadata=interaction_meta,
    )

    # Message 12: System Join
    msg12 = MockMessage(
        1012,
        "",
        user2,
        base_time + datetime.timedelta(minutes=0),
        channel=channel,
        type_name="new_member",
    )
    # Mapping fake type enum
    msg12.type = discord.MessageType.new_member

    # Message 13: System Boost
    msg13 = MockMessage(
        1013,
        "",
        user1,
        base_time + datetime.timedelta(minutes=50),
        channel=channel,
        type_name="premium_guild_subscription",
    )
    # Mapping fake type enum
    msg13.type = discord.MessageType.premium_guild_subscription

    # Update msg5 with timestamp
    msg5.embeds[0].timestamp = base_time

    messages = [
        msg13,
        msg12,
        msg11,
        msg10,
        msg9,
        msg8,
        msg7,
        msg6,
        msg5,
        msg4,
        msg3,
        msg2,
        msg1,
    ]
    # Transcript.export reverses the list if after is None, expecting Newest->Oldest input.
    # So we sort descending (Newest first) to get Oldest first in the output.
    messages.sort(key=lambda x: x.created_at, reverse=True)

    html = await raw_export(channel, messages, guild=guild, language="fr")

    # Correction des avertissements "parser-blocking script"
    # Remplace l'injection via document.write par une balise script standard avec defer
    # (Regex is kept just in case, but base.html now handles defer natively)
    html = re.sub(
        r"<script>\s*document\.write\s*\(\s*['\"]\s*<script\s+src=['\"]([^'\"]+)['\"]\s*>\s*<\\/script>\s*['\"]\s*\)\s*;?\s*</script>",
        r'<script src="\1" defer></script>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    print("Generated test_render.html successfully.")

    # Injection du bouton retour
    back_button = """
    <!-- Back Button (Visible on Top Hover) -->
    <a href="../index.html" id="back-button" class="fixed top-6 left-1/2 -translate-x-1/2 z-[100] bg-[#0a0a0c]/90 border border-white/10 text-white px-6 py-2 rounded-full shadow-2xl backdrop-blur-md transition-all duration-300 opacity-0 -translate-y-full pointer-events-none flex items-center gap-2 font-medium hover:bg-white/10 hover:scale-105">
        <i data-lucide="arrow-left" class="w-4 h-4"></i>
        Retour
    </a>
    """
    html = html.replace("<body>", "<body>" + back_button)

    back_button_script = """
    <script>
        document.addEventListener("DOMContentLoaded", () => {
            lucide.createIcons();
            // 6. Back Button Logic
            const backBtn = document.getElementById('back-button');
            document.addEventListener('mousemove', (e) => {
                if (e.clientY < 100) {
                    backBtn.classList.remove('opacity-0', '-translate-y-full', 'pointer-events-none');
                } else {
                    backBtn.classList.add('opacity-0', '-translate-y-full', 'pointer-events-none');
                }
            });
        });
    </script>
    """
    html = html.replace("</body>", back_button_script + "</body>")

    with open("test_render.html", "w", encoding="utf-8") as f:
        f.write(html)

    # Write to specific path as requested, catching errors if path invalid on this OS
    try:
        output_path = (
            r"C:\Users\xougu\Desktop\Transcript_Site\exemples\exemple_preview.html"
        )
        # Handle drive letter for non-Windows envs if needed or just let it fail gracefully
        if os.name != "nt":
            # Just for safety in linux envs, we skip or print warning,
            # but user specifically asked for this code back.
            # We will try to execute it but catch exception.
            pass

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Generated {output_path} successfully.")
    except Exception as e:
        print(f"Could not write to {output_path}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
