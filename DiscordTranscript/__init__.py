from importlib.metadata import PackageNotFoundError, version

from DiscordTranscript.chat_exporter import (
    AttachmentHandler,
    AttachmentToDataURIHandler,
    AttachmentToDiscordChannelHandler,
    export,
    quick_export,
    raw_export,
)
from DiscordTranscript.construct.custom_colors import (
    DEFAULT_CUSTOM_COLORS,
    generate_custom_colors_file,
    parse_custom_colors_file,
)

try:
    __version__ = version("DiscordTranscript")
except PackageNotFoundError:
    try:
        from DiscordTranscript._version import __version__  # type: ignore
    except ImportError:
        __version__ = "0.0.0-dev"

__all__ = (
    "export",
    "raw_export",
    "quick_export",
    "AttachmentHandler",
    "AttachmentToDataURIHandler",
    "AttachmentToDiscordChannelHandler",
    "generate_custom_colors_file",
    "parse_custom_colors_file",
    "DEFAULT_CUSTOM_COLORS",
)
