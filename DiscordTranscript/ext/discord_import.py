discord_modules = ["nextcord", "disnake", "discord"]
discord = None
discord_errors = None

for module in discord_modules:
    try:
        discord = __import__(module)
        discord.module = module
        # Attempt to import DiscordException, which is a common base for discord errors
        if hasattr(discord, "DiscordException"):
            discord_errors = discord.DiscordException
        elif hasattr(
            discord, "HTTPException"
        ):  # Fallback for older versions or specific error types
            discord_errors = discord.HTTPException
        # Check if the module has an 'errors' submodule and if it contains the exception
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
    # If no specific discord error is found, fallback to generic Exception.
    discord_errors = Exception
