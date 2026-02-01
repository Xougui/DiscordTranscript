import html
import re

from DiscordTranscript.ext.emoji_convert import convert_emoji


class ParseMarkdown:
    """A class to parse markdown in a message.

    Attributes:
        content (str): The content to parse.
        code_blocks_content (list): A list of code blocks in the content.
        placeholders (dict): A dictionary of placeholders to replace.
    """

    def __init__(self, content, placeholders: dict = None):
        """Initializes the ParseMarkdown class.

        Args:
            content (str): The content to parse.
            placeholders (dict, optional): A dictionary of placeholders to replace. Defaults to None.
        """
        self.content = content
        self.code_blocks_content = []
        self.placeholders = placeholders or {}
        self.links_placeholders = {}

    def add_link_placeholder(self, full_tag=None, start_tag=None, end_tag=None):
        """Adds a link placeholder.

        Args:
            full_tag (str, optional): The full link tag. Defaults to None.
            start_tag (str, optional): The start link tag. Defaults to None.
            end_tag (str, optional): The end link tag. Defaults to None.

        Returns:
            str or tuple: The placeholder(s).
        """
        link_id = len(self.links_placeholders)
        if full_tag:
            placeholder = f"%LINK-FULL-{link_id}%"
            self.links_placeholders[placeholder] = full_tag
            return placeholder
        elif start_tag and end_tag:
            start_ph = f"%LINK-START-{link_id}%"
            end_ph = f"%LINK-END-{link_id}%"
            self.links_placeholders[start_ph] = start_tag
            self.links_placeholders[end_ph] = end_tag
            return start_ph, end_ph
        return ""

    def restore_links(self):
        """Restores the links from placeholders."""
        for placeholder, tag in self.links_placeholders.items():
            self.content = self.content.replace(placeholder, tag)

    async def standard_message_flow(self):
        """The standard flow for parsing a message.

        Returns:
            str: The parsed content.
        """
        self.parse_code_block_markdown()
        self.parse_masked_links()
        self.https_http_links()
        self.parse_normal_markdown()

        await self.parse_emoji()
        self.reverse_code_block_markdown()
        self.reverse_tenor_placeholders()
        self.restore_links()
        return self.content

    async def link_embed_flow(self):
        """The flow for parsing a link embed.

        Returns:
            str: The parsed content.
        """
        self.parse_masked_links()
        await self.parse_emoji()
        self.restore_links()

    async def standard_embed_flow(self):
        """The standard flow for parsing an embed.

        Returns:
            str: The parsed content.
        """
        self.parse_code_block_markdown()
        self.https_http_links()
        self.parse_masked_links()
        self.parse_normal_markdown()

        await self.parse_emoji()
        self.reverse_code_block_markdown()
        self.restore_links()
        return self.content

    async def special_embed_flow(self):
        """The flow for parsing a special embed.

        Returns:
            str: The parsed content.
        """
        self.https_http_links()
        self.parse_code_block_markdown()
        self.parse_normal_markdown()

        await self.parse_emoji()
        self.reverse_code_block_markdown()
        self.restore_links()
        return self.content

    async def message_reference_flow(self):
        """The flow for parsing a message reference.

        Returns:
            str: The parsed content.
        """
        self.strip_preserve()
        self.parse_code_block_markdown(reference=True)
        self.parse_normal_markdown()
        self.reverse_code_block_markdown()
        self.parse_br()

        return self.content

    async def special_emoji_flow(self):
        """The flow for parsing a special emoji.

        Returns:
            str: The parsed content.
        """
        await self.parse_emoji()
        return self.content

    def parse_br(self):
        """Parses <br> tags."""
        self.content = self.content.replace("<br>", " ")

    async def parse_emoji(self):
        """Parses emojis."""
        holder = (
            [
                r"&lt;:.*?:(\d*)&gt;",
                '<img class="emoji emoji--small" src="https://cdn.discordapp.com/emojis/%s.png" alt="Emoji">',
            ],
            [
                r"&lt;a:.*?:(\d*)&gt;",
                '<img class="emoji emoji--small" src="https://cdn.discordapp.com/emojis/%s.gif" alt="Emoji">',
            ],
            [
                r"<:.*?:(\d*)>",
                '<img class="emoji emoji--small" src="https://cdn.discordapp.com/emojis/%s.png" alt="Emoji">',
            ],
            [
                r"<a:.*?:(\d*)>",
                '<img class="emoji emoji--small" src="https://cdn.discordapp.com/emojis/%s.gif" alt="Emoji">',
            ],
        )

        self.content = await convert_emoji([word for word in self.content])

        for x in holder:
            p, r = x
            match = re.search(p, self.content)
            while match is not None:
                emoji_id = match.group(1)
                self.content = self.content.replace(
                    self.content[match.start() : match.end()], r % emoji_id
                )
                match = re.search(p, self.content)

    def strip_preserve(self):
        """Strips the preserve tags from the content."""
        p = r'<div class="chatlog__markdown-preserve">(.*)</div>'
        r = "%s"

        pattern = re.compile(p)
        match = re.search(pattern, self.content)
        while match is not None:
            affected_text = match.group(1)
            self.content = self.content.replace(
                self.content[match.start() : match.end()], r % affected_text
            )
            match = re.search(pattern, self.content)

    def order_list_markdown_to_html(self):
        """Converts a markdown ordered list to HTML."""
        lines = self.content.split("\n")
        html = ""
        # Stack of (indent, list_type)
        list_stack = []

        for line in lines:
            match = re.match(r"^(\s*)([-*]|\d+\.)\s+(.+)$", line)
            if match:
                indent_str, bullet, content = match.groups()
                indent = len(indent_str)
                is_ordered = bullet[-1] == '.'
                list_type = "ol" if is_ordered else "ul"

                if not list_stack:
                    # Start new list
                    style = ' style="list-style-type: decimal;"' if is_ordered else ' style="list-style-type: disc;"'
                    style = style[:-1] + '; padding-left: 20px; margin: 0 !important;"'
                    
                    start_attr = ""
                    if is_ordered:
                        try:
                            start_num = int(bullet[:-1])
                            if start_num != 1:
                                start_attr = f' start="{start_num}"'
                        except ValueError:
                            pass

                    html += f'<{list_type} class="markup"{style}{start_attr}>\n'
                    list_stack.append((indent, list_type))
                else:
                    last_indent, last_type = list_stack[-1]
                    
                    if indent > last_indent:
                        # Nested list
                        style = ' style="list-style-type: decimal;"' if is_ordered else ""
                        if not is_ordered:
                            depth = len([t for i, t in list_stack if t == 'ul'])
                            styles = ["disc", "circle", "square"]
                            s_type = styles[depth % 3]
                            style = f' style="list-style-type: {s_type};"'
                        
                        html += f'<{list_type} class="markup"{style}>\n'
                        list_stack.append((indent, list_type))
                    elif indent < last_indent:
                        while list_stack and list_stack[-1][0] > indent:
                            _, ltype = list_stack.pop()
                            html += f"</{ltype}>\n"
                        
                        if list_stack and list_stack[-1][1] != list_type:
                             _, old_type = list_stack.pop()
                             html += f"</{old_type}>\n"
                             style = ' style="list-style-type: decimal;"' if is_ordered else ' style="list-style-type: disc;"'
                             html += f'<{list_type} class="markup"{style}>\n'
                             list_stack.append((indent, list_type))
                    else:
                        if list_stack[-1][1] != list_type:
                             _, old_type = list_stack.pop()
                             html += f"</{old_type}>\n"
                             style = ' style="list-style-type: decimal;"' if is_ordered else ' style="list-style-type: disc;"'
                             html += f'<{list_type} class="markup"{style}>\n'
                             list_stack.append((indent, list_type))

                html += f'<li class="markup">{content.strip()}</li>\n'
            else:
                while list_stack:
                    _, ltype = list_stack.pop()
                    html += f"</{ltype}>\n"
                html += line + "\n"

        while list_stack:
            _, ltype = list_stack.pop()
            html += f"</{ltype}>\n"

        self.content = html

    def parse_normal_markdown(self):
        """Parses normal markdown."""
        self.order_list_markdown_to_html()
        holder = (
            [r"\*\*(.*?)\*\*", "<strong>%s</strong>"],
            [r"__(.*?)__", '<span class="markdown-underline">%s</span>'],
            [r"\*(.*?)\*", "<em><span>%s</span></em>"],
            [r"_(.*?)_", "<em><span>%s</span></em>"],
            [r"~~(.*?)~~", '<span class="markdown-strikethrough">%s</span>'],
            [r"^\s*-#\s+(.*?)$", '<span style="color: #949BA4; font-size: 0.75rem; line-height: 1.375rem;">%s</span>'],
            [r"^\s*###\s(.*?)$", '<h3 style="font-weight: 700; font-size: 1rem; margin: 0.25em 0; line-height: 1.25;">%s</h3>'],
            [r"^\s*##\s(.*?)$", '<h2 style="font-weight: 700; font-size: 1.25rem; margin: 0.25em 0; line-height: 1.25;">%s</h2>'],
            [r"^\s*#\s(.*?)$", '<h1 style="font-weight: 700; font-size: 1.5rem; margin: 0.25em 0; line-height: 1.25;">%s</h1>'],
            [
                r"\|\|(.*?)\|\|",
                '<span class="spoiler spoiler--hidden" onclick="showSpoiler(event, this)"> <span '
                'class="spoiler-text">%s</span></span>',
            ],
        )

        for x in holder:
            p, r = x
            self.content = re.sub(p, lambda m: r.replace("%s", m.group(1)), self.content, flags=re.M)

        # > quote
        lines = self.content.split("\n")
        new_lines = []
        in_quote = False
        in_multiline_quote = False
        quote_content = []
        pattern_single = re.compile(r"^\s*&gt;\s?(.*)")
        pattern_multi = re.compile(r"^\s*&gt;&gt;&gt;\s?(.*)")

        for line in lines:
            if in_multiline_quote:
                quote_content.append(line)
                continue

            match_multi = pattern_multi.match(line)
            if match_multi:
                in_multiline_quote = True
                if in_quote:
                    in_quote = False
                quote_content.append(match_multi.group(1))
                continue

            match_single = pattern_single.match(line)
            if match_single:
                if not in_quote:
                    in_quote = True
                quote_content.append(match_single.group(1))
            else:
                if in_quote:
                    new_lines.append(
                        f'<div class="quote">{"<br>".join(quote_content)}</div>'
                    )
                    quote_content = []
                    in_quote = False
                new_lines.append(line)

        if in_quote or in_multiline_quote:
            new_lines.append(f'<div class="quote">{"<br>".join(quote_content)}</div>')

        self.content = "\n".join(new_lines)

    def parse_code_block_markdown(self, reference=False):
        """Parses code block markdown."""
        # The content of a code block is treated as plain text and should not be parsed for markdown.
        # Therefore, we do not call return_to_markdown on the extracted content.
        markdown_languages = [
            "asciidoc",
            "autohotkey",
            "bash",
            "coffeescript",
            "cpp",
            "cs",
            "css",
            "diff",
            "fix",
            "glsl",
            "ini",
            "json",
            "md",
            "ml",
            "prolog",
            "py",
            "tex",
            "xl",
            "xml",
            "js",
            "html",
        ]
        self.content = re.sub(r"\n", "<br>", self.content)

        # ```code```
        pattern = re.compile(r"```(.*?)```")
        match = re.search(pattern, self.content)
        while match is not None:
            language_class = "nohighlight"
            affected_text = match.group(1)

            for language in markdown_languages:
                if affected_text.lower().startswith(language):
                    language_class = f"language-{language}"
                    _, _, affected_text = affected_text.partition("<br>")

            second_pattern = re.compile(r"^<br>|<br>$")
            second_match = re.search(second_pattern, affected_text)
            while second_match is not None:
                affected_text = re.sub(r"^<br>|<br>$", "", affected_text)
                second_match = re.search(second_pattern, affected_text)
            affected_text = re.sub("  ", "&nbsp;&nbsp;", affected_text)
            # affected_text = html.escape(affected_text)
            self.code_blocks_content.append(affected_text)
            if not reference:
                self.content = self.content.replace(
                    self.content[match.start() : match.end()],
                    '<div class="pre pre--multiline %s">%s</div>'
                    % (language_class, f"%s{len(self.code_blocks_content)}"),
                )
            else:
                self.content = self.content.replace(
                    self.content[match.start() : match.end()],
                    '<span class="pre pre-inline">%s</span>'
                    % f"%s{len(self.code_blocks_content)}",
                )

            match = re.search(pattern, self.content)

        # ``code``
        pattern = re.compile(r"``(.*?)``")
        match = re.search(pattern, self.content)
        while match is not None:
            affected_text = match.group(1)
            # affected_text = html.escape(affected_text)
            self.code_blocks_content.append(affected_text)
            self.content = self.content.replace(
                self.content[match.start() : match.end()],
                '<code class="inline">%s</code>' % f"%s{len(self.code_blocks_content)}",
            )
            match = re.search(pattern, self.content)

        # `code`
        pattern = re.compile(r"`(.*?)`")
        match = re.search(pattern, self.content)
        while match is not None:
            affected_text = match.group(1)
            # affected_text = html.escape(affected_text)
            self.code_blocks_content.append(affected_text)
            self.content = self.content.replace(
                self.content[match.start() : match.end()],
                '<span class="pre pre-inline">%s</span>'
                % f"%s{len(self.code_blocks_content)}",
            )
            match = re.search(pattern, self.content)

        self.content = re.sub(r"<br>", "\n", self.content)

    def reverse_code_block_markdown(self):
        """Reverses the code block markdown parsing."""
        for x in range(len(self.code_blocks_content)):
            self.content = self.content.replace(
                f"%s{x + 1}", self.code_blocks_content[x]
            )

    def reverse_tenor_placeholders(self):
        """Reverses the tenor placeholders."""
        for placeholder, img_tag in self.placeholders.items():
            self.content = self.content.replace(html.escape(placeholder), img_tag)

    def parse_masked_links(self):
        """Parses masked links (e.g. [text](url))."""
        # [Message](Link)
        pattern = re.compile(r"\[(.+?)]\((.+?)\)")
        match = re.search(pattern, self.content)
        while match is not None:
            affected_text = match.group(1)
            affected_url = match.group(2)
            if affected_url.startswith("<") and affected_url.endswith(">"):
                affected_url = affected_url[1:-1]

            start_tag = f'<a href="{affected_url}" style="color: #00a8fc;">'
            end_tag = '</a>'
            start_ph, end_ph = self.add_link_placeholder(start_tag=start_tag, end_tag=end_tag)

            self.content = self.content.replace(
                self.content[match.start() : match.end()],
                f'{start_ph}{affected_text}{end_ph}'
            )
            match = re.search(pattern, self.content)

    @staticmethod
    def order_list_html_to_markdown(content):
        """Converts an HTML ordered list to markdown."""
        lines = content.split("<br>")
        html = ""
        ul_level = -1

        for line in lines:
            if '<ul class="markup">' in line:
                ul_level += 1
                line = line.replace('<ul class="markup">', "")
                if line != "":
                    html += line + "\n"
            elif "</ul>" in line:
                ul_level -= 1
            elif '<li class="markup">' in line:
                match = re.match(r'<li class="markup">(.+?)</li>', line)
                if match:
                    matched_content = match.group(1)
                    spaces = ul_level * 2
                    html += " " * spaces + "-" + matched_content + "\n"
                else:
                    html += line
            else:
                html += line

        return html

    def return_to_markdown(self, content):
        """Returns the content to markdown."""
        # content = self.order_list_html_to_markdown(content)
        holders = (
            [r"<strong>(.*?)</strong>", "**%s**"],
            [r"<em>([^<>]+)</em>", "*%s*"],
            [r"<h1[^>]*>([^<>]+)</h1>", "# %s"],
            [r"<h2[^>]*>([^<>]+)</h2>", "## %s"],
            [r"<h3[^>]*>([^<>]+)</h3>", "### %s"],
            [r'<span style="text-decoration: underline">([^<>]+)</span>', "__%s__"],
            [r'<span style="text-decoration: line-through">([^<>]+)</span>', "~~%s~~"],
            [r'<div class="quote">(.*?)</div>', "> %s"],
            [
                r'<span class="spoiler spoiler--hidden" onclick="showSpoiler\(event, this\)"> <span '
                r'class="spoiler-text">(.*?)<\/span><\/span>',
                "||%s||",
            ],
            [
                r'<span class="unix-timestamp" data-timestamp=".*?" raw-content="(.*?)">.*?</span>',
                "%s",
            ],
        )

        for x in holders:
            p, r = x

            pattern = re.compile(p)
            match = re.search(pattern, content)
            while match is not None:
                affected_text = match.group(1)
                content = content.replace(
                    content[match.start() : match.end()], r % html.escape(affected_text)
                )
                match = re.search(pattern, content)

        pattern = re.compile(r'<a href="(.*?)".*?>(.*?)</a>')
        match = re.search(pattern, content)
        while match is not None:
            affected_url = match.group(1)
            affected_text = match.group(2)
            if affected_url != affected_text:
                content = content.replace(
                    content[match.start() : match.end()],
                    "[%s](%s)" % (affected_text, affected_url),
                )
            else:
                content = content.replace(
                    content[match.start() : match.end()], "%s" % affected_url
                )
            match = re.search(pattern, content)

        return content.lstrip().rstrip()

    def https_http_links(self):
        """Parses https and http links."""
        regex = r"(&lt;https?:\/\/.*?&gt;)|((?<!\]\()https?:\/\/(?:[^\s<&]|&(?!lt;|gt;|quot;))+)"

        def replace_link(match):
            if match.group(1):
                # Wrapped link
                full_match = match.group(1)
                url = full_match[4:-4]
                full_tag = f'<a href="{url}" style="color: #00a8fc;">{url}</a>'
                return self.add_link_placeholder(full_tag=full_tag)

            url = match.group(2)

            # Handle trailing punctuation
            trailing_punctuation = {'.', ',', ':', ')', ']', '}'}
            cleaned_url = url
            suffix = ""

            while True:
                if not cleaned_url:
                    break
                last_char = cleaned_url[-1]
                if last_char in trailing_punctuation:
                    if last_char == ')' and '(' in cleaned_url:
                        break
                    suffix = last_char + suffix
                    cleaned_url = cleaned_url[:-1]
                    continue
                if cleaned_url.endswith("&#39;"):
                    suffix = "&#39;" + suffix
                    cleaned_url = cleaned_url[:-5]
                    continue
                break

            full_tag = f'<a href="{cleaned_url}" style="color: #00a8fc;">{cleaned_url}</a>'
            return self.add_link_placeholder(full_tag=full_tag) + suffix

        self.content = re.sub(regex, replace_link, self.content)
