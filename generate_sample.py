import asyncio
from dataclasses import dataclass, field
import datetime
from pathlib import Path
import platform
import re
from unittest.mock import MagicMock

import discord

from DiscordTranscript import raw_export

# Monkey-patch discord pour supporter les composants V2 pour le mocking
for cls_name in [
    "SectionComponent",
    "TextDisplay",
    "ThumbnailComponent",
    "SeparatorComponent",
    "Container",
]:
    if not hasattr(discord, cls_name):
        setattr(discord, cls_name, type(cls_name, (), {}))


# Mock objects to simulate discord.py models


@dataclass
class MockAsset:
    url: str

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


@dataclass
class MockColor:
    value: int
    r: int = field(init=False)
    g: int = field(init=False)
    b: int = field(init=False)

    def __post_init__(self):
        self.r = (self.value >> 16) & 255
        self.g = (self.value >> 8) & 255
        self.b = self.value & 255

    def __str__(self):
        return f"#{self.value:06x}"


class MockRole:
    def __init__(self, id, name, color=None):
        self.id = id
        self.name = name
        self.color = color if color else MockColor(0xFFFFFF)


class MockUser:
    def __init__(
        self,
        id,
        name,
        discriminator,
        avatar_url,
        bot=False,
        verified_bot=False,
        color=None,
    ):
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
        self.public_flags.verified_bot = verified_bot

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

    async def fetch_message(self, id):
        raise discord.NotFound(MagicMock(), "Not Found")


class MockAttachment:
    def __init__(self, filename, url, size, content_type="image/png"):
        self.filename = filename
        self.url = url
        self.proxy_url = url
        self.size = size
        self.content_type = content_type
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
        video=None,
        provider=None,
        type="rich",
        url=None,
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
        self.url = url
        self.video = video
        self.provider = provider
        self.type = type


class MockEmbedField:
    def __init__(self, name, value, inline):
        self.name = name
        self.value = value
        self.inline = inline


class MockEmbedProxy:
    def __init__(self, url=None, text=None, icon_url=None, name=None, width=None, height=None):
        self.url = url
        self.text = text
        self.icon_url = icon_url
        self.name = name
        self.proxy_icon_url = None
        self.proxy_url = url
        self.width = width
        self.height = height


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


class MockActionRow(discord.ActionRow):
    def __init__(self, children):
        self.children = children


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


class MockContainer(discord.Container):
    def __init__(self, children, accent_color=None):
        self.children = children
        self._accent_color = accent_color

    @property
    def accent_color(self):
        return self._accent_color


class MockSection(discord.SectionComponent):
    def __init__(self, children, accessory=None):
        self.children = children
        self.accessory = accessory


class MockTextDisplay(discord.TextDisplay):
    def __init__(self, content):
        self.content = content


class MockThumbnail(discord.ThumbnailComponent):
    def __init__(self, url):
        self.media = MagicMock()
        self.media.url = url


class MockSeparator(discord.SeparatorComponent):
    def __init__(self):
        pass


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


BACK_BUTTON_HTML = """
    <!-- Back Button (Visible on Top Hover) -->
    <a href="javascript:history.back()" id="back-button" class="fixed top-6 left-1/2 -translate-x-1/2 z-[100] bg-[#0a0a0c]/90 border border-white/10 text-white px-6 py-2 rounded-full shadow-2xl backdrop-blur-md transition-all duration-300 opacity-0 -translate-y-full pointer-events-none flex items-center gap-2 font-medium hover:bg-white/10 hover:scale-105">
        <i data-lucide="arrow-left" class="w-4 h-4"></i>
        Retour
    </a>
    """

BACK_BUTTON_SCRIPT = """
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
        verified_bot=True,
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
        "https://images.freeimages.com/images/large-previews/e69/wadi-rum-desert-4-1058229.jpg?fmt=webp&h=350",
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
    button_disabled = MockButton("Désactivé", MockButtonStyle.secondary, disabled=True)

    action_row_buttons = MockActionRow(
        [button_primary, button_secondary, button_danger, button_link, button_disabled]
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
        "Cool Sticker",
        "https://images.freeimages.com/images/large-previews/003/sushi-roll-1321056.jpg?fmt=webp&h=350",
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
        base_time + datetime.timedelta(minutes=60),
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
        "Ceci est une commande slash d'exemple.",
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
        base_time + datetime.timedelta(minutes=30),
        channel=channel,
        type_name="premium_guild_subscription",
    )
    # Mapping fake type enum
    msg13.type = discord.MessageType.premium_guild_subscription

    # Message 14: Edited Message
    msg14 = MockMessage(
        1014,
        "Ce message a été modifié.",
        user1,
        base_time + datetime.timedelta(minutes=45),
        channel=channel,
    )
    msg14.edited_at = base_time + datetime.timedelta(minutes=46)

    # Message 15: Pinned Message (System)
    msg15 = MockMessage(
        1015,
        "",
        user2,
        base_time + datetime.timedelta(minutes=11),
        channel=channel,
        type_name="pins_add",
    )
    msg15.type = discord.MessageType.pins_add
    msg15.reference = MagicMock(
        message_id=msg4.id, guild_id=guild.id, channel_id=channel.id
    )

    # Message 16: Thread Created (System)
    msg16 = MockMessage(
        1016,
        "Nouveau fil de discussion important",
        user1,
        base_time + datetime.timedelta(minutes=48),
        channel=channel,
        type_name="thread_created",
    )
    msg16.type = discord.MessageType.thread_created

    # Message 17: Audio Attachment
    audio_att = MockAttachment(
        "musique.mp3",
        "https://data.freetouse.com/music/tracks/15baf58e-2e84-43b0-a30a-b147308c8088/file/mp3",
        1024 * 1024,
        content_type="audio/mpeg",
    )
    msg17 = MockMessage(
        1017,
        "Écoutez ce fichier audio :",
        user2,
        base_time + datetime.timedelta(minutes=50),
        attachments=[audio_att],
        channel=channel,
    )

    # Message 18: Video Attachment
    video_att = MockAttachment(
        "video.mp4",
        "https://www.w3schools.com/html/mov_bbb.mp4",
        1024 * 1024 * 5,
        content_type="video/mp4",
    )
    msg18 = MockMessage(
        1018,
        "Regardez cette vidéo :",
        user1,
        base_time + datetime.timedelta(minutes=52),
        attachments=[video_att],
        channel=channel,
    )

    # Message 19: Reply to deleted message
    msg19 = MockMessage(
        1019,
        "Je réponds à un message qui n'existe plus.",
        user2,
        base_time + datetime.timedelta(minutes=55),
        channel=channel,
        reference=MagicMock(
            message_id=999999,  # ID inexistant
            guild_id=guild.id,
            channel_id=channel.id,
        ),
    )

    # Message 20: Spoiler Image
    spoiler_att = MockAttachment(
        "SPOILER_secret.png",
        "https://images.freeimages.com/variants/nDv5dLEb1auNuDied29fLkGp/f4a36f6589a0e50e702740b15352bc00e4bfaf6f58bd4db850e167794d05993d?fmt=webp&h=350",
        1024,
    )
    msg20 = MockMessage(
        1020,
        "Attention, image spoiler ci-dessous :",
        user1,
        base_time + datetime.timedelta(minutes=58),
        attachments=[spoiler_att],
        channel=channel,
    )

    # Message 21: Composants V2 (Container, Section, TextDisplay)
    # Imitation d'une vue type Embed comme demandé

    # Section 1: En-tête avec Titre et Miniature
    text_header = MockTextDisplay(
        "**Panel de Configuration**\n"
        "Gérez vos paramètres utilisateur et vos préférences directement depuis ce message interactif."
    )
    thumb = MockThumbnail("https://lyxios.xouxou-hosting.fr/images/PDP_Lyxios.webp")
    section_header = MockSection([text_header], accessory=thumb)

    # Séparateur
    separator = MockSeparator()

    # Section 2: Informations supplémentaires (Texte seul)
    text_info = MockTextDisplay(
        "**Statut du compte :** ✅ Vérifié\n"
        "**Niveau d'accès :** ⭐ Premium\n"
        "**Dernière connexion :** Il y a 2 heures"
    )
    # Ajout d'un bouton comme accessoire dans la section
    btn_refresh = MockButton("Actualiser", MockButtonStyle.secondary, emoji=MockEmoji("🔄"))
    section_info = MockSection([text_info], accessory=btn_refresh)

    # Section 3: Menu de sélection
    select_v2 = MockSelectMenu(
        "select_v2",
        [
            MockSelectOption(
                "Notifications", "notif", "Gérer les alertes", MockEmoji("🔔")
            ),
            MockSelectOption(
                "Confidentialité",
                "privacy",
                "Paramètres de vie privée",
                MockEmoji("🔒"),
            ),
            MockSelectOption("Thème", "theme", "Changer l'apparence", MockEmoji("🎨")),
        ],
        placeholder="Que souhaitez-vous configurer ?",
    )
    action_row_select = MockActionRow([select_v2])

    # Section 3b: Second Menu de sélection (Langue)
    select_lang = MockSelectMenu(
        "select_lang",
        [
            MockSelectOption("Français", "fr", emoji=MockEmoji("🇫🇷"), default=True),
            MockSelectOption("English", "en", emoji=MockEmoji("🇬🇧")),
            MockSelectOption("Deutsch", "de", emoji=MockEmoji("🇩🇪")),
        ],
        placeholder="Langue / Language",
    )
    action_row_lang = MockActionRow([select_lang])

    # Section 4: Boutons d'action
    btn_save = MockButton("Sauvegarder", MockButtonStyle.success, emoji=MockEmoji("💾"))
    btn_cancel = MockButton("Annuler", MockButtonStyle.secondary)
    btn_help = MockButton(
        "Aide", MockButtonStyle.link, url="https://support.discord.com"
    )
    action_row_buttons = MockActionRow([btn_save, btn_cancel, btn_help])

    # Container contenant tout
    container = MockContainer(
        children=[
            section_header,
            separator,
            section_info,
            separator,
            action_row_select,
            action_row_lang,
            action_row_buttons,
        ],
        accent_color=MockColor(0x5865F2),
    )

    msg21 = MockMessage(
        1021,
        "Voici un exemple avancé utilisant les composants V2 (Containers) :",
        bot_user,
        base_time + datetime.timedelta(minutes=59),
        components=[container],
        channel=channel,
    )

    # Message 22: Message avec un lien
    msg22 = MockMessage(
        1022,
        "Voici un lien vers le dépôt GitHub : https://github.com/Xougui/DiscordTranscript",
        user1,
        base_time + datetime.timedelta(minutes=60),
        channel=channel,
    )

    # Message 23: Embed avec Vidéo (Style YouTube)
    embed_video = MockEmbed(
        title="Never Gonna Give You Up",
        description="The legendary video.",
        color=0xFF0000,
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        video=MockEmbedProxy(url="https://www.youtube.com/embed/dQw4w9WgXcQ", width=560, height=315),
        provider=MockEmbedProxy(name="YouTube", url="https://www.youtube.com"),
        type="video",
    )
    msg23 = MockMessage(
        1023,
        "Voici une vidéo intégrée :",
        user2,
        base_time + datetime.timedelta(minutes=61),
        embeds=[embed_video],
        channel=channel,
    )

    # Message 24: Embed Image Seule (GIF)
    embed_image_only = MockEmbed(
        type="image",
        image=MockEmbedProxy(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExb3V5eGk2eGk2eGk2eGk2eGk2eGk2eGk2eGk2eGk2eGk2/xT4uQulxzV39haRFjG/giphy.gif"),
        color=0x202225,
    )
    msg24 = MockMessage(
        1024,
        "",
        user1,
        base_time + datetime.timedelta(minutes=62),
        embeds=[embed_image_only],
        channel=channel,
    )

    # Message 25: Pièces jointes multiples
    att_text = MockAttachment("notes.txt", "https://example.com/notes.txt", 1024, "text/plain")
    att_img = MockAttachment("screenshot.png", "https://png.pngtree.com/thumb_back/fh260/background/20240522/pngtree-abstract-cloudy-background-beautiful-natural-streaks-of-sky-and-clouds-red-image_15684333.jpg", 5000, "image/png")
    msg25 = MockMessage(
        1025,
        "Voici plusieurs fichiers pour le dossier :",
        user2,
        base_time + datetime.timedelta(minutes=63),
        attachments=[att_text, att_img],
        channel=channel,
    )

    # Message 26: Markdown Avancé
    md_advanced = (
        "# Grand Titre\n"
        "## Sous-titre\n"
        "### Sous-sous-titre\n\n"
        "-# Subtext\n"
        "**Liste numérotée :**\n"
        "1. Premier élément\n"
        "2. Deuxième élément\n"
        "3. Troisième élément\n\n"
        "> Ceci est une citation en bloc.\n"
        "> Elle peut s'étendre sur plusieurs lignes.\n\n"
        "**Liste à puces :**\n"
        "- Liste à puces item 1\n"
        "- Liste à puces item 2\n"
        "  - Sous-item indenté\n\n"
        "Voici un [lien vers Discord](https://discord.com).\n"
        "Et du code inline `print('test')`."
    )
    msg26 = MockMessage(
        1026,
        md_advanced,
        user1,
        base_time + datetime.timedelta(minutes=64),
        channel=channel,
    )

    # Message 27: Contenu Mixte (Texte + Embed + Composants)
    embed_mixed = MockEmbed(
        title="Confirmation requise",
        description="Veuillez confirmer la réception des documents ci-dessus.",
        color=0xF1C40F,
    )
    btn_confirm = MockButton("J'ai reçu", MockButtonStyle.success, emoji=MockEmoji("✅"))
    msg27 = MockMessage(
        1027,
        "Merci de vérifier.",
        bot_user,
        base_time + datetime.timedelta(minutes=65),
        embeds=[embed_mixed],
        components=[MockActionRow([btn_confirm])],
        channel=channel,
    )

    # Message 28: Bloc de code long
    long_code = "```python\n" + "\n".join([f"print('Ligne de code numéro {i}')" for i in range(1, 21)]) + "\n```"
    msg28 = MockMessage(
        1028,
        "Voici un fichier de code plus long :\n" + long_code,
        user1,
        base_time + datetime.timedelta(minutes=66),
        channel=channel,
    )

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
        msg14,
        msg15,
        msg16,
        msg17,
        msg18,
        msg19,
        msg20,
        msg21,
        msg22,
        msg23,
        msg24,
        msg25,
        msg26,
        msg27,
        msg28,
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
    html = html.replace("<body>", "<body>" + BACK_BUTTON_HTML)
    html = html.replace("</body>", BACK_BUTTON_SCRIPT + "</body>")

    hostname = platform.node()

    print(f"Hostname détecté : {hostname}")

    # Gestion des chemins de sortie avec pathlib
    output_filename = "test_render.html"
    local_path = Path(output_filename)

    # 1. Écriture locale (toujours effectuée)
    local_path.write_text(html, encoding="utf-8")
    print(f"Generated local file: {local_path.absolute()}")

    # 2. Écriture vers le chemin spécifique (si le dossier parent existe)
    if hostname == "PC_Xougui":
        dev_path = Path(
            r"C:\Users\xougu\Desktop\Transcript_Site\exemples\exemple_preview.html"
        )

        try:
            if dev_path.parent.exists():
                dev_path.write_text(html, encoding="utf-8")
                print(f"Generated dev path: {dev_path}")
            else:
                print(f"Dev path skipped (directory not found): {dev_path.parent}")
        except Exception as e:
            print(f"Could not write to dev path: {e}")
    else:
        print("Dev path skipped (hostname does not match).")


if __name__ == "__main__":
    asyncio.run(main())
