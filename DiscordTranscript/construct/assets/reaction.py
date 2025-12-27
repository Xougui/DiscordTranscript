import re
from typing import Optional, TYPE_CHECKING
from DiscordTranscript.ext.emoji_convert import convert_emoji
from DiscordTranscript.ext.html_generator import (
    fill_out,
    emoji,
    custom_emoji,
    PARSE_MODE_NONE,
)

if TYPE_CHECKING:
    import discord as discord_typings


class Reaction:
    """A class to represent a Discord reaction.

    Attributes:
        reaction (discord.Reaction): The reaction to represent.
        guild (discord.Guild): The guild the reaction is in.
    """

    def __init__(
        self,
        reaction,
        guild,
        bot: Optional["discord_typings.Client"] = None,
        timezone: str = "UTC",
    ):
        """Initializes the Reaction.

        Args:
            reaction (discord.Reaction): The reaction to represent.
            guild (discord.Guild): The guild the reaction is in.
            bot (Optional[discord.Client]): The bot instance. Defaults to None.
            timezone (str): The timezone to use. Defaults to "UTC".
        """
        self.reaction = reaction
        self.guild = guild
        self.bot = bot
        self.timezone = timezone

    async def flow(self):
        """Builds the reaction and returns the HTML.

        Returns:
            str: The HTML of the reaction.
        """
        await self.build_reaction()

        return self.reaction

    async def build_reaction(self):
        """Builds the reaction's HTML based on its type."""
        if ":" in str(self.reaction.emoji):
            emoji_animated = re.compile(r"&lt;a:.*:.*&gt;")
            if emoji_animated.search(str(self.reaction.emoji)):
                await self.create_discord_reaction("gif")
            else:
                await self.create_discord_reaction("png")
        else:
            await self.create_standard_emoji()

    async def create_discord_reaction(self, emoji_type):
        """Builds a custom Discord reaction.

        Args:
            emoji_type (str): The type of emoji (e.g. "gif", "png").
        """
        pattern = r":.*:(\d*)"
        emoji_id = re.search(pattern, str(self.reaction.emoji)).group(1)
        self.reaction = await fill_out(
            self.guild,
            custom_emoji,
            [
                ("EMOJI", str(emoji_id), PARSE_MODE_NONE),
                ("EMOJI_COUNT", str(self.reaction.count), PARSE_MODE_NONE),
                ("EMOJI_FILE", emoji_type, PARSE_MODE_NONE),
            ],
            bot=self.bot,
            timezone=self.timezone,
        )

    async def create_standard_emoji(self):
        """Builds a standard emoji reaction."""
        react_emoji = await convert_emoji(self.reaction.emoji)
        self.reaction = await fill_out(
            self.guild,
            emoji,
            [
                ("EMOJI", str(react_emoji), PARSE_MODE_NONE),
                ("EMOJI_COUNT", str(self.reaction.count), PARSE_MODE_NONE),
            ],
            bot=self.bot,
            timezone=self.timezone,
        )
