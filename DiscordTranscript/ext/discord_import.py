from typing import Any

discord_modules = ["nextcord", "disnake", "discord"]
discord: Any = None
discord_errors: Any = None

for module in discord_modules:
    try:
        discord = __import__(module)
        setattr(discord, "module", module)  # noqa: B010

        if hasattr(discord, "DiscordException"):
            discord_errors = discord.DiscordException
        elif hasattr(discord, "HTTPException"):
            discord_errors = discord.HTTPException

        elif hasattr(discord, "errors"):
            if hasattr(discord.errors, "DiscordException"):
                discord_errors = discord.errors.DiscordException
            elif hasattr(discord.errors, "HTTPException"):
                discord_errors = discord.errors.HTTPException
        break
    except ImportError:
        continue

if discord is None:
    raise ImportError(
        "Could not find any of the discord modules: nextcord, disnake, or discord"
    )

if discord_errors is None:
    try:
        from discord import DiscordException as discord_errors
    except ImportError:
        try:
            from discord import HTTPException as discord_errors
        except ImportError:

            class GenericDiscordError(Exception):
                pass

            discord_errors = GenericDiscordError
