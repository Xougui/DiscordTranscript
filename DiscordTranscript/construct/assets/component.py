from typing import TYPE_CHECKING, Optional

from DiscordTranscript.ext.discord_import import discord
from DiscordTranscript.ext.discord_utils import DiscordUtils
from DiscordTranscript.ext.html_generator import (
    PARSE_MODE_EMOJI,
    PARSE_MODE_MARKDOWN,
    PARSE_MODE_NONE,
    component_button,
    component_container,
    component_menu,
    component_menu_options,
    component_menu_options_emoji,
    component_section,
    component_separator,
    component_text_display,
    component_thumbnail,
    fill_out,
)

if TYPE_CHECKING:
    import discord as discord_typings


class Component:
    """A class to represent a Discord component.

    Attributes:
        styles (dict): A dictionary of button styles.
        components (str): The HTML for the components.
        menus (str): The HTML for the menus.
        buttons (str): The HTML for the buttons.
        menu_div_id (int): The ID of the menu div.
        component (discord.Component): The component to represent.
        guild (discord.Guild): The guild the component is in.
    """

    styles = {
        "primary": "#5865F2",
        "secondary": "#4E5058",
        "success": "#248046",
        "danger": "#DA373C",
        "blurple": "#5865F2",
        "grey": "#4E5058",
        "gray": "#4E5058",
        "green": "#248046",
        "red": "#DA373C",
        "link": "#4E5058",
    }

    components: str = ""
    menus: str = ""
    buttons: str = ""
    menu_div_id: int = 0

    def __init__(
        self,
        component,
        guild,
        bot: Optional["discord_typings.Client"] = None,
        timezone: str = "UTC",
    ):
        """Initializes the Component.

        Args:
            component (discord.Component): The component to represent.
            guild (discord.Guild): The guild the component is in.
            bot (Optional[discord.Client]): The bot instance. Defaults to None.
            timezone (str): The timezone to use. Defaults to "UTC".
        """
        self.component = component
        self.guild = guild
        self.bot = bot
        self.timezone = timezone

    async def build_component(self, c):
        """Builds a component.

        Args:
            c (discord.Component): The component to build.
        """
        if isinstance(c, discord.Button):
            await self.build_button(c)
        elif isinstance(c, discord.SelectMenu):
            await self.build_menu(c)
            Component.menu_div_id += 1
        elif isinstance(c, discord.SectionComponent):
            self.components += await self.build_section(c)
        elif isinstance(c, discord.TextDisplay):
            self.components += await self.build_text_display(c)
        elif isinstance(c, discord.ThumbnailComponent):
            self.components += await self.build_thumbnail(c)
        elif isinstance(c, discord.SeparatorComponent):
            self.components += await self.build_separator(c)
        elif isinstance(c, discord.Container):
            self.components += await self.build_container(c)
        elif isinstance(c, discord.ActionRow):
            # Recursively handle nested ActionRows if any (though usually they are top level)
            # But here we are processing children of a top level component.
            # If an ActionRow is nested inside a Container, we need to handle it.
            # But ActionRow logic in `flow` separates buttons and menus.
            # Here we want to append them to `self.components` instead of separating them
            # if we are inside a structured layout.

            # Create a new Component instance to handle this ActionRow's children
            sub_component = Component(c, self.guild, self.bot, self.timezone)
            self.components += await sub_component.flow()

    async def build_container(self, c):
        children_html = ""
        # Access c.children or c.components if children not available (discord.py internals)
        children = getattr(c, "children", [])

        for child in children:
            if isinstance(child, discord.ActionRow):
                sub_comp = Component(child, self.guild, self.bot, self.timezone)
                children_html += await sub_comp.flow()
            else:
                # It's a Section or other component
                # We can use a temporary component instance to build it
                # But `build_component` adds to `self.components` etc.
                # Using a dummy ActionRow might fail if we need to pass a valid component
                # But we can pass None if we don't use it, but __init__ stores it.
                # Let's pass the child itself as the component
                temp = Component(child, self.guild, self.bot, self.timezone)
                # Wait, Component flow expects children.
                # We want to call build_component directly on the child.
                # But build_component is an instance method that updates self.components

                # So:
                await temp.build_component(child)
                # Merge results
                children_html += temp.components
                if temp.menus:
                    children_html += (
                        f'<div class="chatlog__components">{temp.menus}</div>'
                    )
                if temp.buttons:
                    children_html += (
                        f'<div class="chatlog__components">{temp.buttons}</div>'
                    )

        accent_color = str(c.accent_color) if c.accent_color else "#1e1f22"

        return await fill_out(
            self.guild,
            component_container,
            [
                ("ACCENT_COLOR", accent_color, PARSE_MODE_NONE),
                ("CHILDREN", children_html, PARSE_MODE_NONE),
            ],
            bot=self.bot,
            timezone=self.timezone,
        )

    async def build_section(self, c):
        children_html = ""
        children = getattr(c, "children", [])
        for child in children:
            temp = Component(child, self.guild, self.bot, self.timezone)
            await temp.build_component(child)
            children_html += temp.components
            if temp.menus:
                children_html += (
                    f'<div class="chatlog__components">{temp.menus}</div>'
                )
            if temp.buttons:
                children_html += (
                    f'<div class="chatlog__components">{temp.buttons}</div>'
                )

        accessory_html = ""
        if c.accessory:
            temp = Component(c.accessory, self.guild, self.bot, self.timezone)
            await temp.build_component(c.accessory)
            accessory_html += temp.components
            # Accessories like Buttons need to be wrapped if they are buttons?
            # `build_button` adds to `self.buttons`.
            if temp.menus:
                accessory_html += (
                    f'<div class="chatlog__components">{temp.menus}</div>'
                )
            if temp.buttons:
                accessory_html += (
                    f'<div class="chatlog__components">{temp.buttons}</div>'
                )

        return await fill_out(
            self.guild,
            component_section,
            [
                ("CHILDREN", children_html, PARSE_MODE_NONE),
                ("ACCESSORY", accessory_html, PARSE_MODE_NONE),
            ],
            bot=self.bot,
            timezone=self.timezone,
        )

    async def build_text_display(self, c):
        return await fill_out(
            self.guild,
            component_text_display,
            [
                ("CONTENT", str(c.content), PARSE_MODE_MARKDOWN),
            ],
            bot=self.bot,
            timezone=self.timezone,
        )

    async def build_thumbnail(self, c):
        return await fill_out(
            self.guild,
            component_thumbnail,
            [
                ("IMAGE_URL", str(c.media.url), PARSE_MODE_NONE),
            ],
            bot=self.bot,
            timezone=self.timezone,
        )

    async def build_separator(self, c):
        return await fill_out(
            self.guild,
            component_separator,
            [],
            bot=self.bot,
            timezone=self.timezone,
        )

    async def build_button(self, c):
        """Builds a button.

        Args:
            c (discord.Button): The button to build.
        """
        if c.url:
            url = str(c.url)
            target = ' target="_blank" rel="noopener noreferrer"'
            icon = str(DiscordUtils.button_external_link)
        else:
            url = "javascript:;"
            target = ""
            icon = ""

        label = str(c.label) if c.label else ""
        style = self.styles[str(c.style).split(".")[1]]
        emoji = str(c.emoji) if c.emoji else ""

        self.buttons += await fill_out(
            self.guild,
            component_button,
            [
                (
                    "DISABLED",
                    "chatlog__component-disabled" if c.disabled else "",
                    PARSE_MODE_NONE,
                ),
                ("URL", url, PARSE_MODE_NONE),
                ("LABEL", label, PARSE_MODE_MARKDOWN),
                ("EMOJI", emoji, PARSE_MODE_EMOJI),
                ("ICON", icon, PARSE_MODE_NONE),
                ("TARGET", target, PARSE_MODE_NONE),
                ("STYLE", style, PARSE_MODE_NONE),
            ],
            bot=self.bot,
            timezone=self.timezone,
        )

    async def build_menu(self, c):
        """Builds a menu.

        Args:
            c (discord.SelectMenu): The menu to build.
        """
        placeholder = c.placeholder if c.placeholder else ""
        options = c.options
        content = ""

        if not c.disabled:
            content = await self.build_menu_options(options)

        self.menus += await fill_out(
            self.guild,
            component_menu,
            [
                (
                    "DISABLED",
                    "chatlog__component-disabled" if c.disabled else "",
                    PARSE_MODE_NONE,
                ),
                ("ID", str(self.menu_div_id), PARSE_MODE_NONE),
                ("PLACEHOLDER", str(placeholder), PARSE_MODE_MARKDOWN),
                ("CONTENT", str(content), PARSE_MODE_NONE),
                ("ICON", DiscordUtils.interaction_dropdown_icon, PARSE_MODE_NONE),
            ],
            bot=self.bot,
            timezone=self.timezone,
        )

    async def build_menu_options(self, options):
        """Builds the options for a menu.

        Args:
            options (list): The options to build.

        Returns:
            str: The HTML for the menu options.
        """
        content = []
        for option in options:
            if option.emoji:
                content.append(
                    await fill_out(
                        self.guild,
                        component_menu_options_emoji,
                        [
                            ("EMOJI", str(option.emoji), PARSE_MODE_EMOJI),
                            ("TITLE", str(option.label), PARSE_MODE_MARKDOWN),
                            (
                                "DESCRIPTION",
                                str(option.description) if option.description else "",
                                PARSE_MODE_MARKDOWN,
                            ),
                        ],
                        bot=self.bot,
                        timezone=self.timezone,
                    )
                )
            else:
                content.append(
                    await fill_out(
                        self.guild,
                        component_menu_options,
                        [
                            ("TITLE", str(option.label), PARSE_MODE_MARKDOWN),
                            (
                                "DESCRIPTION",
                                str(option.description) if option.description else "",
                                PARSE_MODE_MARKDOWN,
                            ),
                        ],
                        bot=self.bot,
                        timezone=self.timezone,
                    )
                )

        if content:
            content = f'<div id="dropdownMenu{self.menu_div_id}" class="dropdownContent">{"".join(content)}</div>'

        return content

    async def flow(self):
        """Builds the components and returns the HTML.

        Returns:
            str: The HTML for the components.
        """
        if isinstance(self.component, discord.Container):
            self.components += await self.build_container(self.component)
        else:
            children = getattr(self.component, "children", [])
            for c in children:
                await self.build_component(c)

            if self.menus:
                self.components += (
                    f'<div class="chatlog__components">{self.menus}</div>'
                )

            if self.buttons:
                self.components += (
                    f'<div class="chatlog__components">{self.buttons}</div>'
                )

        return self.components
