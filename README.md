# Discord Channel To HTML Transcripts

<div align="center">
    <p>
        <a href="https://pypi.org/project/DiscordTranscript/">
            <img src="https://img.shields.io/pypi/v/DiscordTranscript.svg" alt="PyPI Version">
        </a>
        <a href="https://pypi.org/project/DiscordTranscript/">
            <img src="https://img.shields.io/pypi/pyversions/DiscordTranscript.svg" alt="PyPI Python Versions">
        </a>
    </p>
</div>

Une librairie Python pour créer des transcriptions de salons Discord au format HTML.

*Le code de base provient de [py-discord-html-transcripts](https://github.com/FroostySnoowman/py-discord-html-transcripts) et a été adapté et amélioré.*

---

## Aperçu

![Aperçu 1](screenshots/1.png)
![Aperçu 2](screenshots/2.png)
![Aperçu 3](screenshots/3.png)

---

## Table des matières

- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
  - [Utilisation de base](#utilisation-de-base)
  - [Utilisation personnalisable](#utilisation-personnalisable)
  - [Utilisation brute (raw)](#utilisation-brute-raw)
- [Exemples avancés](#exemples-avancés)
  - [Sauvegarder les pièces jointes localement](#sauvegarder-les-pièces-jointes-localement)
  - [Exporter un intervalle de dates spécifique](#exporter-un-intervalle-de-dates-spécifique)
  - [Utilisation dans un Cog](#utilisation-dans-un-cog)
  - [Utilisation avec les commandes d'application](#utilisation-avec-les-commandes-dapplication)
  - [Gestion des erreurs](#gestion-des-erreurs)

---

## Prérequis

- `discord.py` v2.4.0 ou plus récent

---

## Installation

Pour installer la librairie, exécutez la commande suivante :

```sh
pip install DiscordTranscript
```

**NOTE :** Cette librairie est une extension pour `discord.py` et ne fonctionne pas de manière autonome. Vous devez avoir un bot `discord.py` fonctionnel pour l'utiliser.

---

## Utilisation

Il existe trois méthodes principales pour exporter une conversation : `quick_export`, `export`, et `raw_export`.

### Utilisation de base

La fonction `.quick_export()` est la manière la plus simple d'utiliser la librairie. Elle récupère l'historique du salon, génère la transcription, puis la publie directement dans le même salon.

**Arguments requis :**
- `channel`: L'objet `discord.TextChannel` à exporter.

**Arguments optionnels :**
- `bot`: L'objet `commands.Bot` pour récupérer les informations sur les membres qui ne sont plus sur le serveur.

**Retourne :**
- `discord.Message`: Le message contenant la transcription.

**Exemple :**
```python
import discord
import DiscordTranscript as chat_exporter
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def save(ctx: commands.Context):
    await chat_exporter.quick_export(ctx.channel, bot=bot)

bot.run("VOTRE_TOKEN")
```

### Utilisation personnalisable

La fonction `.export()` est la méthode la plus flexible. Elle permet de personnaliser la transcription avec plusieurs options.

**Arguments requis :**
- `channel`: L'objet `discord.TextChannel` à exporter.

**Arguments optionnels :**
- `limit`: Le nombre maximum de messages à récupérer (par défaut : illimité).
- `tz_info`: Le fuseau horaire à utiliser (ex: "Europe/Paris"). [Liste des fuseaux horaires](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List).
- `military_time`: `True` pour utiliser le format 24h, `False` pour le format 12h (par défaut : `True`).
- `fancy_times`: `True` pour afficher des temps relatifs (ex: "Aujourd'hui à..."), `False` sinon (par défaut : `True`).
- `before`: Un objet `datetime.datetime` pour récupérer les messages avant cette date.
- `after`: Un objet `datetime.datetime` pour récupérer les messages après cette date.
- `bot`: L'objet `commands.Bot`.

**Retourne :**
- `str`: Le contenu HTML de la transcription.

**Exemple :**
```python
import io
import discord
import DiscordTranscript as chat_exporter
from discord.ext import commands

# ... (initialisation du bot)

@bot.command()
async def save_custom(ctx: commands.Context):
    transcript = await chat_exporter.export(
        ctx.channel,
        limit=100,
        tz_info="Europe/Paris",
        military_time=True,
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

### Utilisation brute (raw)

La fonction `.raw_export()` permet de créer une transcription à partir d'une liste de messages que vous fournissez.

**Arguments requis :**
- `channel`: L'objet `discord.TextChannel` (utilisé pour les en-têtes).
- `messages`: Une liste d'objets `discord.Message`.

**Arguments optionnels :**
- `tz_info`, `military_time`, `fancy_times`, `bot`.

**Retourne :**
- `str`: Le contenu HTML de la transcription.

**Exemple :**
```python
import io
import discord
import DiscordTranscript as chat_exporter
from discord.ext import commands

# ... (initialisation du bot)

@bot.command()
async def save_purged(ctx: commands.Context):
    deleted_messages = await ctx.channel.purge(limit=50)

    transcript = await chat_exporter.raw_export(
        ctx.channel,
        messages=deleted_messages,
        bot=bot,
    )

    if transcript is None:
        return

    transcript_file = discord.File(
        io.BytesIO(transcript.encode()),
        filename=f"purged-transcript-{ctx.channel.name}.html",
    )

    await ctx.send("Voici la transcription des messages supprimés :", file=transcript_file)
```

---

## Exemples avancés

### Sauvegarder les pièces jointes localement

Par défaut, les pièces jointes sont liées via leur URL Discord. Pour les sauvegarder localement, utilisez `AttachmentToLocalFileHostHandler`.

**Exemple :**
```python
import io
import os
import discord
import DiscordTranscript as chat_exporter
from DiscordTranscript.construct.attachment_handler import AttachmentToLocalFileHostHandler
from discord.ext import commands

# ... (initialisation du bot)

@bot.command()
async def save_local_attachments(ctx: commands.Context):
    if not os.path.exists(f"attachments/{ctx.channel.id}"):
        os.makedirs(f"attachments/{ctx.channel.id}")

    transcript = await chat_exporter.export(
        ctx.channel,
        attachment_handler=AttachmentToLocalFileHostHandler(
            path=f"attachments/{ctx.channel.id}"
        ),
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

### Exporter un intervalle de dates spécifique

Utilisez les paramètres `before` et `after` pour exporter une période précise.

**Exemple :**
```python
import io
import discord
import datetime
import DiscordTranscript as chat_exporter
from discord.ext import commands

# ... (initialisation du bot)

@bot.command()
async def save_last_week(ctx: commands.Context):
    after_date = datetime.datetime.now() - datetime.timedelta(days=7)

    transcript = await chat_exporter.export(
        ctx.channel,
        after=after_date,
        bot=bot,
    )

    if transcript is None:
        return

    transcript_file = discord.File(
        io.BytesIO(transcript.encode()),
        filename=f"transcript-last-week-{ctx.channel.name}.html",
    )

    await ctx.send(file=transcript_file)
```

### Utilisation dans un Cog

Organisez votre code en utilisant des Cogs.

**Exemple :**
```python
# cogs/transcript_cog.py
import io
import discord
import DiscordTranscript as chat_exporter
from discord.ext import commands

class TranscriptCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def save_in_cog(self, ctx: commands.Context):
        transcript = await chat_exporter.export(
            ctx.channel,
            bot=self.bot,
        )

        if transcript is None:
            return

        transcript_file = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{ctx.channel.name}.html",
        )

        await ctx.send(file=transcript_file)

async def setup(bot: commands.Bot):
    await bot.add_cog(TranscriptCog(bot))
```

### Utilisation avec les commandes d'application

Utilisez `chat-exporter` avec les commandes slash.

**Exemple :**
```python
import io
import discord
import DiscordTranscript as chat_exporter
from discord import app_commands

# ... (initialisation du bot)

@bot.tree.command(name="save", description="Sauvegarde la conversation actuelle.")
@app_commands.describe(channel="Le salon à sauvegarder (optionnel, défaut: salon actuel)")
async def save_slash(interaction: discord.Interaction, channel: discord.TextChannel = None):
    await interaction.response.defer()
    
    if channel is None:
        channel = interaction.channel

    transcript = await chat_exporter.export(
        channel,
        bot=bot,
    )

    if transcript is None:
        await interaction.followup.send("Impossible de sauvegarder la conversation.", ephemeral=True)
        return

    transcript_file = discord.File(
        io.BytesIO(transcript.encode()),
        filename=f"transcript-{channel.name}.html",
    )

    await interaction.followup.send(file=transcript_file)

# N'oubliez pas de synchroniser l'arbre de commandes
# @bot.event
# async def on_ready():
#     await bot.tree.sync()
```

### Gestion des erreurs

Il est important de gérer les erreurs potentielles, comme les permissions manquantes.

**Exemple :**
```python
import io
import discord
import DiscordTranscript as chat_exporter
from discord.ext import commands

# ... (initialisation du bot)

@bot.command()
async def save_safe(ctx: commands.Context):
    try:
        transcript = await chat_exporter.export(
            ctx.channel,
            bot=bot,
        )
    except discord.Forbidden:
        await ctx.send("Je n'ai pas la permission de lire l'historique de ce salon.")
        return
    except Exception as e:
        await ctx.send(f"Une erreur est survenue : {e}")
        return

    if transcript is None:
        return

    transcript_file = discord.File(
        io.BytesIO(transcript.encode()),
        filename=f"transcript-{ctx.channel.name}.html",
    )

    await ctx.send(file=transcript_file)
```