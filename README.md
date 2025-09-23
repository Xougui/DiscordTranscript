# Discord Channel To HTML Transcripts

<div align="center">
    <p>
        <a href="https://pypi.org/project/DiscordTranscript/">
            <img src="https://img.shields.io/pypi/dm/DiscordTranscript" alt="PyPI Downloads">
        </a>
        <a href="https://github.com/Xougui/DiscordTranscript/">
            <img src="https://img.shields.io/badge/GitHub-DiscordTranscript-green.svg?logo=github" alt="GitHub Repo">
        </a>
        <a href="https://github.com/Xougui/DiscordTranscript/">
            <img src="https://img.shields.io/github/commit-activity/t/Xougui/DiscordTranscript?logo=github" alt="Commit Activity">
        </a>
        <a href="https://github.com/Xougui/DiscordTranscript/">
            <img src="https://img.shields.io/github/last-commit/Xougui/DiscordTranscript/main?logo=github" alt="Last Commit Branch">
        </a>
        <a href="https://pypi.org/project/DiscordTranscript/">
            <img src="https://img.shields.io/pypi/v/DiscordTranscript.svg?logo=pypi&logoColor=ffffff" alt="PyPI Version">
        </a>
        <a href="https://pypi.org/search/?q=&o=&c=Programming+Language+%3A%3A+Python+%3A%3A+3.6&c=Programming+Language+%3A%3A+Python+%3A%3A+3.7&c=Programming+Language+%3A%3A+Python+%3A%3A+3.8&c=Programming+Language+%3A%3A+Python+%3A%3A+3.9&c=Programming+Language+%3A%3A+Python+%3A%3A+3.10&c=Programming+Language+%3A%3A+Python+%3A%3A+3.11&c=Programming+Language+%3A%3A+Python+%3A%3A+3.12&c=Programming+Language+%3A%3A+Python+%3A%3A+3.13">
            <img src="https://img.shields.io/pypi/pyversions/DiscordTranscript.svg?logo=python&logoColor=ffffff" alt="PyPI Python Versions">
        </a>
    </p>
</div>

## Purpose

A Python library for creating HTML transcripts of Discord channels. This is useful for logging, archiving, or sharing conversations from a Discord server.

*The base code comes from [py-discord-html-transcripts](https://github.com/FroostySnoowman/py-discord-html-transcripts) and has been adapted and improved.*

---

## Preview

![Preview 1](https://github.com/Xougui/DiscordTranscript/blob/main/screenshots/1.png?raw=true)
![Preview 2](https://github.com/Xougui/DiscordTranscript/blob/main/screenshots/2.png?raw=true)
![Preview 3](https://github.com/Xougui/DiscordTranscript/blob/main/screenshots/3.png?raw=true)

---

## 🇫🇷 Documentation en Français


<details>
<summary>🇫🇷 Documentation en Français</summary>

## Table des matières

- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Exemples](#exemples)
- [Paramètres](#paramètres)
- [Contribuer](#contribuer)
- [Licence](#licence)

---

## <a id="prérequis"></a>Prérequis

-   Python 3.6 ou plus récent
-   `discord.py` v2.4.0 ou plus récent (ou un fork compatible comme `nextcord` ou `disnake`)

---

## <a id="installation"></a>Installation

Pour installer la librairie, exécutez la commande suivante :

```sh
pip install DiscordTranscript
```

**NOTE :** Cette librairie est une extension pour `discord.py` et ne fonctionne pas de manière autonome. Vous devez avoir un bot `discord.py` fonctionnel pour l'utiliser.

---

## <a id="utilisation"></a>Utilisation

Il existe trois méthodes principales pour exporter une conversation : `quick_export`, `export`, et `raw_export`.

-   `quick_export`: La manière la plus simple d'utiliser la librairie. Elle récupère l'historique du salon, génère la transcription, puis la publie directement dans le même salon.
-   `export`: La méthode la plus flexible. Elle permet de personnaliser la transcription avec plusieurs options.
-   `raw_export`: Permet de créer une transcription à partir d'une liste de messages que vous fournissez.

---

## <a id="exemples"></a>Exemples

### Utilisation de base

<details>
<summary>Exemple</summary>

```python
import discord
import DiscordTranscript
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def save(ctx: commands.Context):
    await DiscordTranscript.quick_export(ctx.channel, bot=bot)

bot.run("VOTRE_TOKEN")
```
</details>

### Utilisation personnalisable

<details>
<summary>Exemple</summary>

```python
import io
import discord
import DiscordTranscript
from discord.ext import commands

# ... (initialisation du bot)

@bot.command()
async def save_custom(ctx: commands.Context):
    transcript = await DiscordTranscript.export(
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
</details>

### Utilisation brute (raw)

<details>
<summary>Exemple</summary>

```python
import io
import discord
import DiscordTranscript
from discord.ext import commands

# ... (initialisation du bot)

@bot.command()
async def save_purged(ctx: commands.Context):
    deleted_messages = await ctx.channel.purge(limit=50)

    transcript = await DiscordTranscript.raw_export(
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
</details>

### Sauvegarder les pièces jointes localement

<details>
<summary>Exemple</summary>

```python
import io
import os
import discord
import DiscordTranscript
from DiscordTranscript.construct.attachment_handler import AttachmentToLocalFileHostHandler
from discord.ext import commands

# ... (initialisation du bot)

@bot.command()
async def save_local_attachments(ctx: commands.Context):
    if not os.path.exists(f"attachments/{ctx.channel.id}"):
        os.makedirs(f"attachments/{ctx.channel.id}")

    transcript = await DiscordTranscript.export(
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
</details>

---
## <a id="paramètres"></a>Paramètres

Voici une liste des paramètres que vous pouvez utiliser dans les fonctions `export()` et `raw_export()` pour personnaliser vos transcriptions.

| Paramètre | Type | Description | Défaut |
| --- | --- | --- | --- |
| `limit` | `int` | Le nombre maximum de messages à récupérer. | `None` (illimité) |
| `before` | `datetime.datetime` | Récupère les messages avant cette date. | `None` |
| `after` | `datetime.datetime` | Récupère les messages après cette date. | `None` |
| `tz_info` | `str` | Le fuseau horaire à utiliser pour les horodatages. Doit être un nom de la base de données TZ (ex: "Europe/Paris"). | `"UTC"` |
| `military_time` | `bool` | Si `True`, utilise le format 24h. Si `False`, utilise le format 12h (AM/PM). | `True` |
| `fancy_times` | `bool` | Si `True`, utilise des horodatages relatifs (ex: "Aujourd'hui à..."). Si `False`, affiche la date complète. | `True` |
| `bot` | `discord.Client` | L'instance de votre bot. Nécessaire pour résoudre les informations des utilisateurs qui ont quitté le serveur. | `None` |
| `attachment_handler` | `AttachmentHandler` | Un gestionnaire pour contrôler la façon dont les pièces jointes sont sauvegardées. Voir l'exemple [Sauvegarder les pièces jointes localement](#sauvegarder-les-pièces-jointes-localement). | `None` (les liens des pièces jointes pointent vers le CDN de Discord) |

---

## <a id="contribuer"></a>Contribuer

Les contributions sont les bienvenues ! Veuillez ouvrir une issue ou soumettre une pull request sur le [dépôt GitHub](https://github.com/Xougui/DiscordTranscript).

## <a id="licence"></a>Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

</details>

---

## 🇬🇧 English Documentation


<details>
<summary>🇬🇧 English Documentation</summary>

## Table of Contents

- [Prerequisites](#prerequisites-en)
- [Installation](#installation-en)
- [Usage](#usage-en)
- [Examples](#examples-en)
- [Parameters](#parameters-en)
- [Contributing](#contributing-en)
- [License](#license-en)

---

## <a id="prerequisites-en"></a>Prerequisites

-   Python 3.6 or newer
-   `discord.py` v2.4.0 or newer (or a compatible fork like `nextcord` or `disnake`)

---

## <a id="installation-en"></a>Installation

To install the library, run the following command:

```sh
pip install DiscordTranscript
```

**NOTE:** This library is an extension for `discord.py` and does not work standalone. You must have a functional `discord.py` bot to use it.

---

## <a id="usage-en"></a>Usage

There are three main methods for exporting a conversation: `quick_export`, `export`, and `raw_export`.

-   `quick_export`: The simplest way to use the library. It retrieves the channel's history, generates the transcript, and then publishes it directly in the same channel.
-   `export`: The most flexible method. It allows you to customize the transcript with several options.
-   `raw_export`: Allows you to create a transcript from a list of messages you provide.

---

## <a id="examples-en"></a>Examples

### Basic Usage

<details>
<summary>Example</summary>

```python
import discord
import DiscordTranscript
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def save(ctx: commands.Context):
    await DiscordTranscript.quick_export(ctx.channel, bot=bot)

bot.run("YOUR_TOKEN")
```
</details>

### Customizable Usage

<details>
<summary>Example</summary>

```python
import io
import discord
import DiscordTranscript
from discord.ext import commands

# ... (bot initialization)

@bot.command()
async def save_custom(ctx: commands.Context):
    transcript = await DiscordTranscript.export(
        ctx.channel,
        limit=100,
        tz_info="America/New_York",
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
</details>

### Raw Usage

<details>
<summary>Example</summary>

```python
import io
import discord
import DiscordTranscript
from discord.ext import commands

# ... (bot initialization)

@bot.command()
async def save_purged(ctx: commands.Context):
    deleted_messages = await ctx.channel.purge(limit=50)

    transcript = await DiscordTranscript.raw_export(
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

    await ctx.send("Here is the transcript of the deleted messages:", file=transcript_file)
```
</details>

### Saving Attachments Locally

<details>
<summary>Example</summary>

```python
import io
import os
import discord
import DiscordTranscript
from DiscordTranscript.construct.attachment_handler import AttachmentToLocalFileHostHandler
from discord.ext import commands

# ... (bot initialization)

@bot.command()
async def save_local_attachments(ctx: commands.Context):
    if not os.path.exists(f"attachments/{ctx.channel.id}"):
        os.makedirs(f"attachments/{ctx.channel.id}")

    transcript = await DiscordTranscript.export(
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
</details>

---

## <a id="parameters-en"></a>Parameters

Here is a list of parameters you can use in the `export()` and `raw_export()` functions to customize your transcripts.

| Parameter | Type | Description | Default |
| --- | --- | --- | --- |
| `limit` | `int` | The maximum number of messages to retrieve. | `None` (unlimited) |
| `before` | `datetime.datetime` | Retrieves messages before this date. | `None` |
| `after` | `datetime.datetime` | Retrieves messages after this date. | `None` |
| `tz_info` | `str` | The timezone to use for timestamps. Must be a TZ database name (e.g., "America/New_York"). | `"UTC"` |
| `military_time` | `bool` | If `True`, uses 24h format. If `False`, uses 12h format (AM/PM). | `True` |
| `fancy_times` | `bool` | If `True`, uses relative timestamps (e.g., "Today at..."). If `False`, displays the full date. | `True` |
| `bot` | `discord.Client` | Your bot's instance. Necessary to resolve user information for members who have left the server. | `None` |
| `attachment_handler`| `AttachmentHandler` | A handler to control how attachments are saved. See the [Saving Attachments Locally](#saving-attachments-locally-en) example. | `None` (attachment links point to Discord's CDN) |

---

## <a id="contributing-en"></a>Contributing

Contributions are welcome! Please open an issue or submit a pull request on the [GitHub repository](https://github.com/Xougui/DiscordTranscript).

## <a id="license-en"></a>License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

</details>
