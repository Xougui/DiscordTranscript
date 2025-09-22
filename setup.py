from setuptools import setup, find_packages

setup(
    name="DiscordTranscript",
    version="0.1.0",
    author="Xougui",
    author_email="xougui.7@gmail.com",
    description="A Discord chat exporter that is easy to use and customizable. // Un exporteur de chat Discord facile à utiliser et personnalisable.",
    long_description=open("README.md", encoding="utf-8").read(),
    project_urls={
        "Source Code (GitHub)": "https://github.com/Xougui/DiscordTranscript"
    },
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Natural Language :: French",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    license="GPL-3.0-only",
    python_requires=">=3.6",
    install_requires=[
        "aiohttp",
        "pytz",
        "grapheme",
        "emoji",
        "discord.py",
    ],
    keywords=['archive', 'backup', 'channel-exporter', 'chat', 'chat-archive', 'chat exporter', 'chat-logs', 'discord', 'discord-api', 'discord-archive', 'discord-backup', 'discord-bot', 'discord-channel', 'discord-channel-exporter', 'discord-channel-history', 'discord-channel-logs', 'discord-chat', 'discord chat exporter', 'discord-export', 'discord-history', 'discord-html', 'discord-logs', 'discord-message-export', 'discord-messages', 'discord-transcript', 'discordpy', 'disnake', 'export', 'export-chat', 'export-discord', 'file', 'html', 'html-generator', 'html transcript', 'logs', 'message-archive', 'nextcord', 'pycord', 'transcript'],
)