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
- [Obtenir une clé API Tenor](#obtaining-a-tenor-api-key)

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

### Intégrer les pièces jointes dans le HTML

<details>
<summary>Exemple</summary>

```python
import io
import discord
import DiscordTranscript
from DiscordTranscript.construct.attachment_handler import AttachmentToDataURIHandler
from discord.ext import commands

# ... (initialisation du bot)

@bot.command()
async def save_with_embedded_attachments(ctx: commands.Context):
    transcript = await DiscordTranscript.export(
        ctx.channel,
        attachment_handler=AttachmentToDataURIHandler(),
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
| `messages` | `List[discord.Message]` | Une liste de messages à utiliser pour la transcription. | `None` |
| `limit` | `int` | Le nombre maximum de messages à récupérer. | `None` (illimité) |
| `before` | `datetime.datetime` | Récupère les messages avant cette date. | `None` |
| `after` | `datetime.datetime` | Récupère les messages après cette date. | `None` |
| `tz_info` | `str` | Le fuseau horaire à utiliser pour les horodatages. Doit être un nom de la base de données TZ (ex: "Europe/Paris"). | `"UTC"` |
| `military_time` | `bool` | Si `True`, utilise le format 24h. Si `False`, utilise le format 12h (AM/PM). | `True` |
| `fancy_times` | `bool` | Si `True`, utilise des horodatages relatifs (ex: "Aujourd'hui à..."). Si `False`, affiche la date complète. | `True` |
| `bot` | `discord.Client` | L'instance de votre bot. Nécessaire pour résoudre les informations des utilisateurs qui ont quitté le serveur. | `None` |
| `guild`| `discord.Guild` | L'instance de votre serveur. Nécessaire pour résoudre les informations des membres (rôles, couleurs, etc.). | `None` |
| `attachment_handler` | `AttachmentHandler` | Un gestionnaire pour contrôler la façon dont les pièces jointes sont traitées. Voir l'exemple [Intégrer les pièces jointes dans le HTML](#intégrer-les-pièces-jointes-dans-le-html). | `None` (les liens des pièces jointes pointent vers le CDN de Discord) |
| `tenor_api_key` | `str` | Votre clé API Tenor pour afficher les GIFs. | `None` |

**Note :** Le paramètre `messages` est uniquement disponible pour la fonction `raw_export()`.

### Exemples de paramètres

Voici comment vous pouvez utiliser les paramètres pour personnaliser vos transcriptions.

- **`messages`**: Pour créer une transcription à partir d'une liste de messages que vous avez déjà. (Uniquement pour `raw_export`)
  ```python
  # Récupère les 50 derniers messages
  my_messages = await ctx.channel.history(limit=50).flatten()

  transcript = await DiscordTranscript.raw_export(
      ctx.channel,
      messages=my_messages, # Fournit la liste de messages
      bot=bot,
  )
  ```

- **`limit`**: Pour limiter le nombre de messages à 100.
  ```python
  transcript = await DiscordTranscript.export(
      ctx.channel,
      limit=100, # Limite à 100 messages
      bot=bot,
  )
  ```

- **`before` et `after`**: Pour exporter les messages d'une période spécifique.
  ```python
  import datetime

  transcript = await DiscordTranscript.export(
      ctx.channel,
      # Exportera les messages envoyés entre le 10 et le 20 juin 2023
      after=datetime.datetime(2023, 6, 10),  # Après le 10 juin 2023
      before=datetime.datetime(2023, 6, 20), # Avant le 20 juin 2023
      bot=bot,
  )
  ```

- **`tz_info`**: Pour afficher les heures en fonction d'un fuseau horaire (ex: heure de Paris).
  ```python
  transcript = await DiscordTranscript.export(
      ctx.channel,
      tz_info="Europe/Paris", # Fuseau horaire de Paris
      bot=bot,
  )
  ```

- **`military_time`**: Pour utiliser le format 12h (AM/PM) au lieu du format 24h.
  ```python
  transcript = await DiscordTranscript.export(
      ctx.channel,
      military_time=False, # Affiche 1:00 PM au lieu de 13:00
      bot=bot,
  )
  ```

- **`fancy_times`**: Pour afficher la date complète au lieu de "Aujourd'hui à...".
  ```python
  transcript = await DiscordTranscript.export(
      ctx.channel,
      fancy_times=False, # Affiche la date complète (ex: 23/09/2025)
      bot=bot,
  )
  ```

- **`bot`**: Pour résoudre les informations des utilisateurs (même s'ils ont quitté le serveur).
  ```python
  transcript = await DiscordTranscript.export(
      ctx.channel,
      bot=bot, # Fournit l'instance du bot
  )
  ```

- **`guild`**: Pour vous assurer que les rôles et les couleurs des membres sont corrects.
  ```python
  transcript = await DiscordTranscript.export(
      ctx.channel,
      guild=ctx.guild, # Fournit l'instance du serveur
      bot=bot,
  )
  ```

- **`attachment_handler`**: Pour intégrer les pièces jointes directement dans le fichier HTML.
  ```python
  from DiscordTranscript.construct.attachment_handler import AttachmentToDataURIHandler

  transcript = await DiscordTranscript.export(
      ctx.channel,
      # Intègre les pièces jointes en tant que Data URIs
      attachment_handler=AttachmentToDataURIHandler(),
      bot=bot,
  )
  ```

- **`tenor_api_key`**: Pour afficher les GIFs Tenor directement dans la transcription.
  ```python
  transcript = await DiscordTranscript.export(
      ctx.channel,
      tenor_api_key="VOTRE_CLÉ_API_TENOR", # Fournit votre clé API Tenor
      bot=bot,
  )
  ```

---

## <a id="obtaining-a-tenor-api-key"></a>Obtenir une clé API Tenor

Pour utiliser la fonctionnalité d'affichage des GIFs Tenor, vous devez fournir une clé API Tenor. **Suivez attentivement le [guide de démarrage rapide de Tenor](https://developers.google.com/tenor/guides/quickstart) pour en obtenir une.**

1.  **Connectez-vous à la [console Google Cloud](https://console.cloud.google.com/)**.
2.  **Créez un nouveau projet** (ou sélectionnez-en un existant).
3.  **Activez l'API Tenor** :
    -   Dans le menu de navigation, allez dans `APIs & Services` > `Bibliothèque`.
    -   Recherchez `Tenor API` et activez-la pour votre projet.
4.  **Générez une clé API** :
    -   Allez dans `APIs & Services` > `Identifiants`.
    -   Cliquez sur `Créer des identifiants` et sélectionnez `Clé API`.
5.  **Copiez votre clé** et utilisez-la dans le paramètre `tenor_api_key`.

Il est recommandé de restreindre votre clé API pour éviter toute utilisation non autorisée. Vous pouvez le faire depuis la page `Identifiants`.

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
- [Getting a Tenor API Key](#getting-a-tenor-api-key-en)

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

### Embedding Attachments in HTML

<details>
<summary>Example</summary>

```python
import io
import discord
import DiscordTranscript
from DiscordTranscript.construct.attachment_handler import AttachmentToDataURIHandler
from discord.ext import commands

# ... (bot initialization)

@bot.command()
async def save_with_embedded_attachments(ctx: commands.Context):
    transcript = await DiscordTranscript.export(
        ctx.channel,
        attachment_handler=AttachmentToDataURIHandler(),
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
| `messages` | `List[discord.Message]` | A list of messages to use for the transcript. | `None` |
| `limit` | `int` | The maximum number of messages to retrieve. | `None` (unlimited) |
| `before` | `datetime.datetime` | Retrieves messages before this date. | `None` |
| `after` | `datetime.datetime` | Retrieves messages after this date. | `None` |
| `tz_info` | `str` | The timezone to use for timestamps. Must be a TZ database name (e.g., "America/New_York"). | `"UTC"` |
| `military_time` | `bool` | If `True`, uses 24h format. If `False`, uses 12h format (AM/PM). | `True` |
| `fancy_times` | `bool` | If `True`, uses relative timestamps (e.g., "Today at..."). If `False`, displays the full date. | `True` |
| `bot` | `discord.Client` | Your bot's instance. Necessary to resolve user information for members who have left the server. | `None` |
| `guild`| `discord.Guild` | Your server's instance. Necessary to resolve member information (roles, colors, etc.). | `None` |
| `attachment_handler`| `AttachmentHandler` | A handler to control how attachments are processed. See the [Embedding Attachments in HTML](#embedding-attachments-in-html) example. | `None` (attachment links point to Discord's CDN) |
| `tenor_api_key` | `str` | Your Tenor API key to display GIFs. | `None` |

**Note:** The `messages` parameter is only available for the `raw_export()` function.

### Parameter Examples

Here’s how you can use the parameters to customize your transcripts.

- **`messages`**: To create a transcript from a list of messages you already have. (Only for `raw_export`)
  ```python
  # Fetches the last 50 messages
  my_messages = await ctx.channel.history(limit=50).flatten()

  transcript = await DiscordTranscript.raw_export(
      ctx.channel,
      messages=my_messages, # Provide the list of messages
      bot=bot,
  )
  ```

- **`limit`**: To limit the number of messages to 100.
  ```python
  transcript = await DiscordTranscript.export(
      ctx.channel,
      limit=100, # Limit to 100 messages
      bot=bot,
  )
  ```

- **`before` and `after`**: To export messages from a specific period.
  ```python
  import datetime

  transcript = await DiscordTranscript.export(
      ctx.channel,
      # Will export messages sent between June 10th and June 20th, 2023
      after=datetime.datetime(2023, 6, 10),  # After June 10, 2023
      before=datetime.datetime(2023, 6, 20), # Before June 20, 2023
      bot=bot,
  )
  ```

- **`tz_info`**: To display times in a specific timezone (e.g., New York time).
  ```python
  transcript = await DiscordTranscript.export(
      ctx.channel,
      tz_info="America/New_York", # New York timezone
      bot=bot,
  )
  ```

- **`military_time`**: To use 12-hour format (AM/PM) instead of 24-hour format.
  ```python
  transcript = await DiscordTranscript.export(
      ctx.channel,
      military_time=False, # Displays 1:00 PM instead of 13:00
      bot=bot,
  )
  ```

- **`fancy_times`**: To display the full date instead of "Today at...".
  ```python
  transcript = await DiscordTranscript.export(
      ctx.channel,
      fancy_times=False, # Displays the full date (e.g., 09/23/2025)
      bot=bot,
  )
  ```

- **`bot`**: To resolve user information (even if they have left the server).
  ```python
  transcript = await DiscordTranscript.export(
      ctx.channel,
      bot=bot, # Provide the bot instance
  )
  ```

- **`guild`**: To ensure member roles and colors are correct.
  ```python
  transcript = await DiscordTranscript.export(
      ctx.channel,
      guild=ctx.guild, # Provide the guild instance
      bot=bot,
  )
  ```

- **`attachment_handler`**: To embed attachments directly into the HTML file.
  ```python
  from DiscordTranscript.construct.attachment_handler import AttachmentToDataURIHandler

  transcript = await DiscordTranscript.export(
      ctx.channel,
      # Embeds attachments as Data URIs
      attachment_handler=AttachmentToDataURIHandler(),
      bot=bot,
  )
  ```

- **`tenor_api_key`**: To display Tenor GIFs directly in the transcript.
  ```python
  transcript = await DiscordTranscript.export(
      ctx.channel,
      tenor_api_key="YOUR_TENOR_API_KEY", # Provide your Tenor API key
      bot=bot,
  )
  ```

---

## <a id="getting-a-tenor-api-key-en"></a>Getting a Tenor API Key

To use the Tenor GIF display feature, you need to provide a Tenor API key. **Carefully follow the [Tenor quickstart guide](https://developers.google.com/tenor/guides/quickstart) to get one.**

1.  **Log in to the [Google Cloud console](https://console.cloud.google.com/)**.
2.  **Create a new project** (or select an existing one).
3.  **Enable the Tenor API**:
    -   In the navigation menu, go to `APIs & Services` > `Library`.
    -   Search for `Tenor API` and enable it for your project.
4.  **Generate an API key**:
    -   Go to `APIs & Services` > `Credentials`.
    -   Click `Create credentials` and select `API key`.
5.  **Copy your key** and use it in the `tenor_api_key` parameter.

It is recommended to restrict your API key to prevent unauthorized use. You can do this from the `Credentials` page.

</details>