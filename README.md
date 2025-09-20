# discord-html-transcripts

`discord-html-transcripts` est une bibliothèque Python pour générer des transcriptions HTML de canaux Discord.

## Installation

Vous pouvez installer la bibliothèque en utilisant `pip`:

```bash
pip install discord-html-transcripts
```

## Utilisation

Voici comment vous pouvez utiliser `discord-html-transcripts` avec votre bot `discord.py`.

### Exemple de base

```python
import discord
from discord.ext import commands
import discord_html_transcripts as dht

intents = discord.Intents.default()
intents.message_content = True # Nécessaire pour accéder au contenu des messages
intents.members = True # Nécessaire pour accéder aux membres (pour les noms d'utilisateur, etc.)

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}')

@bot.command()
async def transcript(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = ctx.channel

    # Crée la transcription HTML
    transcript_html = await dht.create_transcript(channel)

    # Enregistre la transcription dans un fichier
    with open(f"{channel.name}_transcript.html", "w", encoding="utf-8") as f:
        f.write(transcript_html)

    await ctx.send(f"La transcription du canal '{channel.name}' a été sauvegardée dans '{channel.name}_transcript.html'")

bot.run("YOUR_BOT_TOKEN")
```

### Options avancées

Le paramètre `options` de `create_transcript` permet de personnaliser la transcription.

-   `limit`: Le nombre maximum de messages à transcrire (par défaut, tous les messages).
-   `save_images`: Si `True`, les images jointes et les images d'embed seront encodées en base64 et intégrées directement dans le fichier HTML. Cela rend le fichier plus grand mais autonome.

```python
import discord
from discord.ext import commands
import discord_html_transcripts as dht

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}')

@bot.command()
async def transcript_with_images(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = ctx.channel

    # Crée la transcription HTML en intégrant les images
    options = {
        "save_images": True,
        "limit": 100 # Transcrit les 100 derniers messages
    }
    transcript_html = await dht.create_transcript(channel, options=options)

    with open(f"{channel.name}_transcript_with_images.html", "w", encoding="utf-8") as f:
        f.write(transcript_html)

    await ctx.send(f"La transcription du canal '{channel.name}' (avec images) a été sauvegardée.")

bot.run("YOUR_BOT_TOKEN")
```

## Référence de l'API

### `discord_html_transcripts.create_transcript(channel: discord.TextChannel, options: dict = None) -> str`

Crée une transcription HTML d'un canal Discord.

-   `channel`: L'objet `discord.TextChannel` à transcrire.
-   `options`: Un dictionnaire d'options facultatives :
    -   `limit` (int): Le nombre maximum de messages à récupérer.
    -   `save_images` (bool): Si `True`, les images seront encodées en base64 et intégrées.

Retourne une chaîne de caractères contenant le code HTML de la transcription.

### `discord_html_transcripts.generate_from_messages(messages: list[discord.Message], channel: discord.TextChannel, options: dict = None) -> str`

Génère une transcription HTML à partir d'une liste de messages existante. Cette fonction est utilisée en interne par `create_transcript` mais peut être utilisée directement si vous avez déjà une liste de messages.

-   `messages`: Une liste d'objets `discord.Message`.
-   `channel`: L'objet `discord.TextChannel` d'où proviennent les messages.
-   `options`: Un dictionnaire d'options facultatives (identique à `create_transcript`).

Retourne une chaîne de caractères contenant le code HTML de la transcription.