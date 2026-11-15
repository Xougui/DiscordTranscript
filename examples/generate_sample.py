import asyncio
from dataclasses import dataclass, field
import datetime
from pathlib import Path
import platform
import re
import sys
from unittest.mock import MagicMock

# Prioritize workspace directory over site-packages
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import discord  # noqa: E402

from DiscordTranscript import raw_export  # noqa: E402

for cls_name in [
    "SectionComponent",
    "TextDisplay",
    "ThumbnailComponent",
    "SeparatorComponent",
    "Container",
]:
    if not hasattr(discord, cls_name):
        setattr(discord, cls_name, type(cls_name, (), {}))


LYXIOS_LOGO = (
    "data:image/svg+xml,%3csvg%20xmlns='http://www.w3.org/2000/svg'%20width='512'%20height='512'%20fill='none'%3e"
    "%3cg%20clip-path='url(%23a)'%3e%3cmask%20id='b'%20width='512'%20height='512'%20x='0'%20y='0'%20maskUnits='userSpaceOnUse'%20style='mask-type:alpha'%3e"
    "%3ccircle%20cx='256'%20cy='256'%20r='256'%20fill='%23d9d9d9'/%3e%3c/mask%3e%3cg%20mask='url(%23b)'%3e"
    "%3cpath%20fill='url(%23c)'%20d='M512%200H0v512h512z'/%3e%3c/g%3e"
    "%3cpath%20fill='%23fff'%20d='M80.407%20202.868c3.557-9.307%2014.056-14.037%2022.887-9.423%2028.304%2014.791%2052.918%2038.269%2071.222%2068.184%2018.781%2030.696%2030.085%2066.807%2032.829%20104.386C208.069%20375.93%20199.941%20384%20190%20384h-27.754c-9.942%200-17.907-8.079-18.886-17.971-2.583-26.092-10.72-50.525-23.157-70.852-11.256-18.396-25.229-32.203-40.164-41.394-8.447-5.198-13.175-15.478-9.634-24.743zm351.186%200c-3.557-9.307-14.056-14.037-22.887-9.423-28.304%2014.791-52.918%2038.269-71.222%2068.184-18.781%2030.696-30.085%2066.807-32.829%20104.386C303.931%20375.93%20312.059%20384%20322%20384h27.754c9.942%200%2017.907-8.079%2018.886-17.971%202.583-26.092%2010.72-50.525%2023.157-70.852%2011.256-18.396%2025.229-32.203%2040.164-41.394%208.447-5.198%2013.175-15.478%209.634-24.743zM251.504%20359.164c-68.934-135.535-78.89-159.768-.054-227.3%202.587-2.217%206.513-2.217%209.1%200%2078.836%2067.532%2068.88%2091.765-.054%20227.3-1.853%203.643-7.139%203.643-8.992%200'/%3e%3c/g%3e"
    "%3cdefs%3e%3clinearGradient%20id='c'%20x1='211.558'%20x2='300.442'%20y1='508.109'%20y2='3.891'%20gradientUnits='userSpaceOnUse'%3e"
    "%3cstop%20stop-color='%23105666'/%3e%3cstop%20offset='.1'%20stop-color='%2317595f'/%3e%3cstop%20offset='.2'%20stop-color='%231e5d5a'/%3e"
    "%3cstop%20offset='.3'%20stop-color='%23236055'/%3e%3cstop%20offset='.4'%20stop-color='%23286250'/%3e%3cstop%20offset='.5'%20stop-color='%232d654d'/%3e"
    "%3cstop%20offset='.6'%20stop-color='%2330664a'/%3e%3cstop%20offset='.7'%20stop-color='%23336847'/%3e%3cstop%20offset='.8'%20stop-color='%23356946'/%3e"
    "%3cstop%20offset='.9'%20stop-color='%23366945'/%3e%3cstop%20offset='1'%20stop-color='%23376a45'/%3e%3c/linearGradient%3e"
    "%3cclipPath%20id='a'%3e%3cpath%20fill='%23fff'%20d='M0%200h512v512H0z'/%3e%3c/clipPath%3e%3c/defs%3e%3c/svg%3e"
)


@dataclass
class MockAsset:
    url: str

    def __str__(self):
        return self.url


class MockGuild:
    def __init__(self):
        self.id = 123456789
        self.name = "Serveur de Démonstration"
        self.icon = "https://cdn.discordapp.com/embed/avatars/0.png"
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
    def __init__(self, filename, url, size, content_type="image/png", text=None):
        self.filename = filename
        self.url = url
        self.proxy_url = url
        self.size = size
        self.content_type = content_type
        self.height = 100
        self.width = 100
        self.text = text
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
    def __init__(
        self, url=None, text=None, icon_url=None, name=None, width=None, height=None
    ):
        self.url = url
        self.text = text
        self.icon_url = icon_url
        self.name = name
        self.proxy_icon_url = None
        self.proxy_url = url
        self.width = width
        self.height = height


class MockButton(discord.Button):
    def __init__(self, label, style, url=None, emoji=None, disabled=False):
        self.label = label
        self.style = style
        self.url = url
        self.emoji = emoji
        self.disabled = disabled

        self._underlying = MagicMock()


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


async def main():
    guild = MockGuild()
    channel = MockChannel()
    channel.guild = guild

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
        LYXIOS_LOGO,
        bot=True,
        verified_bot=True,
        color=MockColor(0x5865F2),
    )

    base_time = datetime.datetime.now() - datetime.timedelta(hours=1)

    msg1 = MockMessage(
        1001,
        "Salut tout le monde ! Bienvenue sur le canal de test. Voici un exemple complet de transcript.",
        user1,
        base_time + datetime.timedelta(seconds=30),
        channel=channel,
    )

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

    attachment = MockAttachment(
        "photo_vacances.png",
        "https://picsum.photos/id/1018/800/600",
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
            icon_url=LYXIOS_LOGO,
            url="https://github.com/Xougui/DiscordTranscript",
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

    sticker = MockSticker(
        "Cool Sticker",
        "https://picsum.photos/id/1025/300/300",
    )
    msg8 = MockMessage(
        1008,
        "",
        user1,
        base_time + datetime.timedelta(minutes=25),
        stickers=[sticker],
        channel=channel,
    )

    reaction1 = MockReaction("👍", 10)
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

    msg10 = MockMessage(
        1010,
        "Voici une mention de rôle : <@&999>",
        user1,
        base_time + datetime.timedelta(minutes=35),
        channel=channel,
    )

    interaction_meta = MockInteractionMetadata(user1, "exemple")
    msg11 = MockMessage(
        1011,
        "Ceci est une commande slash d'exemple.",
        bot_user,
        base_time + datetime.timedelta(minutes=40),
        channel=channel,
        interaction_metadata=interaction_meta,
    )

    msg12 = MockMessage(
        1012,
        "",
        user2,
        base_time + datetime.timedelta(minutes=0),
        channel=channel,
        type_name="new_member",
    )

    msg12.type = discord.MessageType.new_member

    msg13 = MockMessage(
        1013,
        "",
        user1,
        base_time + datetime.timedelta(minutes=30),
        channel=channel,
        type_name="premium_guild_subscription",
    )

    msg13.type = discord.MessageType.premium_guild_subscription

    msg14 = MockMessage(
        1014,
        "Ce message a été modifié.",
        user1,
        base_time + datetime.timedelta(minutes=45),
        channel=channel,
    )
    msg14.edited_at = base_time + datetime.timedelta(minutes=46)

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

    msg16 = MockMessage(
        1016,
        "Nouveau fil de discussion important",
        user1,
        base_time + datetime.timedelta(minutes=48),
        channel=channel,
        type_name="thread_created",
    )
    msg16.type = discord.MessageType.thread_created

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

    msg19 = MockMessage(
        1019,
        "Je réponds à un message qui n'existe plus.",
        user2,
        base_time + datetime.timedelta(minutes=55),
        channel=channel,
        reference=MagicMock(
            message_id=999999,
            guild_id=guild.id,
            channel_id=channel.id,
        ),
    )

    spoiler_att = MockAttachment(
        "SPOILER_secret.png",
        "https://picsum.photos/id/1069/800/600",
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

    text_header = MockTextDisplay(
        "**Panel de Configuration**\n"
        "Gérez vos paramètres utilisateur et vos préférences directement depuis ce message interactif."
    )
    thumb = MockThumbnail(LYXIOS_LOGO)
    section_header = MockSection([text_header], accessory=thumb)

    separator = MockSeparator()

    text_info = MockTextDisplay(
        "**Statut du compte :** ✅ Vérifié\n"
        "**Niveau d'accès :** ⭐ Premium\n"
        "**Dernière connexion :** Il y a 2 heures"
    )

    btn_refresh = MockButton(
        "Actualiser", MockButtonStyle.secondary, emoji=MockEmoji("🔄")
    )
    section_info = MockSection([text_info], accessory=btn_refresh)

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

    btn_save = MockButton("Sauvegarder", MockButtonStyle.success, emoji=MockEmoji("💾"))
    btn_cancel = MockButton("Annuler", MockButtonStyle.secondary)
    btn_help = MockButton(
        "Aide", MockButtonStyle.link, url="https://support.discord.com"
    )
    action_row_buttons = MockActionRow([btn_save, btn_cancel, btn_help])

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

    msg22 = MockMessage(
        1022,
        "Voici un lien vers le dépôt GitHub : https://github.com/Xougui/DiscordTranscript",
        user1,
        base_time + datetime.timedelta(minutes=60),
        channel=channel,
    )

    embed_video = MockEmbed(
        title="Never Gonna Give You Up",
        description="The legendary video.",
        color=0xFF0000,
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        video=MockEmbedProxy(
            url="https://www.youtube.com/embed/dQw4w9WgXcQ", width=560, height=315
        ),
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

    embed_image_only = MockEmbed(
        type="image",
        image=MockEmbedProxy(
            url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExb3V5eGk2eGk2eGk2eGk2eGk2eGk2eGk2eGk2eGk2eGk2/xT4uQulxzV39haRFjG/giphy.gif"
        ),
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

    text_sample_content = (
        "De tout temps, l'homme a tenté de comprendre puis de reproduire l'extraordinaire machine qu'est l'être humain. "
        "Les premiers automates nous font sourire aujourd'hui. Les premiers ordinateurs également, mais un peu moins. "
        "Et lorsqu'un certain McCullogn, aidé de Pitts, invente en 1943 le premier neurone formel, on ne rigole plus. "
        'L\'ordinateur est devenu capable de reproduire des neurones artificiels. Le "complexe de Frankenstein" va alors freiner les recherches. '
        "On commence à entendre parler du concept d'Intelligence Artificielle, plus connu sous les termes d'IA. Cela fait peur.\n\n"
        "De tout temps, l'homme a tenté de comprendre puis de reproduire l'extraordinaire machine qu'est l'être humain. "
        "Les premiers automates nous font sourire aujourd'hui. Les premiers ordinateurs également, mais un peu moins. "
        "Et lorsqu'un certain McCullogn, aidé de Pitts, invente en 1943 le premier neurone formel, on ne rigole plus. "
        'L\'ordinateur est devenu capable de reproduire des neurones artificiels. Le "complexe de Frankenstein" va alors freiner les recherches. '
        "On commence à entendre parler du concept d'Intelligence Artificielle, plus connu sous les termes d'IA. Cela fait peur.\n\n"
        "Cela ressemblait aux gros ordinateurs que David avait pu voir dans des films de science fiction. Beaucoup de petites lumières "
        "indiquaient qu'il était en fonction. À la base, une sorte d'aquarium avait été installé tout autour. Certainement le système de "
        "refroidissement car des bulles montaient sans cesse, preuve que l'eau était en ébullition. Soudain, David resta bouche bée. "
        "Une voix caverneuse sortie des écrans où venait de s'afficher le mot « Prélude ».\n\n"
        "David comprenait très bien où voulait en venir Prélude. Lorsqu'il l'avait créé, il détestait ce monde. S'il avait eu la possibilité "
        "de le changer, il l'aurait certainement fait. Il l'aurait fait en pensé, mais pas en geste. David n'était pas du genre méchant. "
        "Jamais il n'aurait fait de mal à qui que ce soit, mais il avait certainement mis cette idée dans la programmation de Prélude sans le vouloir.\n\n"
        "Le seul moyen de le stopper serait d'arrêter tous les ordinateurs, ce qui aurait les mêmes conséquences que de laisser Prélude lancer "
        "les bombes. Depuis longtemps, toutes les installations à risque étaient contrôlées par des ordinateurs. Si l'on stoppait les "
        "ordinateurs, les centrales nucléaires s'emballeraient, les silos nucléaires cracheraient leur mort sur toute la planète. "
        "Bien entendu, l'économie mondiale dirigée par la bourse, s'effondrerait. David ne savait plus quoi faire et, manifestement, "
        "tous les militaires présents dans la salle comptaient sur lui pour résoudre cette crise.\n\n"
        "En 1975, John Holland construisit un système artificiel qui s'appuyait sur les principes de sélection de Darwin et sur les méthodes "
        "de combinaison des gènes de Mendel. L'Algorithme Génétique, ou GA, était né. Un renouveau de l'Intelligence Artificielle allait voir"
    )

    att_text = MockAttachment(
        "message.txt",
        "https://raw.githubusercontent.com/Xougui/DiscordTranscript/main/README.md",
        9216,
        "text/plain",
        text=text_sample_content,
    )
    att_img = MockAttachment(
        "screenshot.png",
        "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800",
        5000,
        "image/png",
    )
    msg25 = MockMessage(
        1025,
        "Voici plusieurs fichiers pour le dossier :",
        user2,
        base_time + datetime.timedelta(minutes=63),
        attachments=[att_text, att_img],
        channel=channel,
    )

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

    embed_mixed = MockEmbed(
        title="Confirmation requise",
        description="Veuillez confirmer la réception des documents ci-dessus.",
        color=0xF1C40F,
    )
    btn_confirm = MockButton(
        "J'ai reçu", MockButtonStyle.success, emoji=MockEmoji("✅")
    )
    msg27 = MockMessage(
        1027,
        "Merci de vérifier.",
        bot_user,
        base_time + datetime.timedelta(minutes=65),
        embeds=[embed_mixed],
        components=[MockActionRow([btn_confirm])],
        channel=channel,
    )

    long_code = (
        "```python\n"
        + "\n".join([f"print('Ligne de code numéro {i}')" for i in range(1, 21)])
        + "\n```"
    )
    msg28 = MockMessage(
        1028,
        "Voici un fichier de code plus long :\n" + long_code,
        user1,
        base_time + datetime.timedelta(minutes=66),
        channel=channel,
    )

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

    messages.sort(key=lambda x: x.created_at, reverse=True)

    html = await raw_export(
        channel,
        messages,
        guild=guild,
        military_time=True,
        tz_info="UTC",
        language="fr",
    )

    html = re.sub(
        r"<script>\s*document\.write\s*\(\s*['\"]\s*<script\s+src=['\"]([^'\"]+)['\"]\s*>\s*<\\/script>\s*['\"]\s*\)\s*;?\s*</script>",
        r'<script src="\1" defer></script>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    print("Generated test_render.html successfully.")

    hostname = platform.node()

    print(f"Hostname détecté : {hostname}")

    output_dir = Path(__file__).parent
    output_dir.mkdir(exist_ok=True)
    local_path = output_dir / "test_render.html"

    local_path.write_text(html, encoding="utf-8")
    print(f"Generated local file: {local_path.absolute()}")

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
