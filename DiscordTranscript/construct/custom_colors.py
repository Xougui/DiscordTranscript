import os
from pathlib import Path

DEFAULT_CUSTOM_COLORS: dict[str, str] = {
    # Buttons / Accent colors
    "discord-blurple": "#5865F2",
    "discord-blurple-hover": "#4752C4",
    "discord-green": "#23A55A",
    "discord-green-hover": "#1A7F42",
    "discord-red": "#F23F43",
    "discord-red-hover": "#A1282C",
    "discord-grey": "#4E5058",
    "discord-grey-hover": "#6D6F78",
    # Backgrounds
    "background-primary": "#313338",
    "background-secondary": "#2b2d31",
    "background-tertiary": "#1e1f22",
    "background-floating": "#232428",
    # Text and UI elements
    "text-white": "#FFFFFF",
    "text-normal": "#dbdee1",
    "text-muted": "#949ba4",
    "discord-text-placeholder": "#dbdee1",
    "discord-icon-color": "#dbdee1",
    "discord-component-bg": "#2B2D31",
    "discord-component-hover": "#404249",
    "discord-border-color": "#1E1F22",
}

_CUSTOM_COLORS_TEMPLATE: str = """# ==============================================================================
# Fichier de configuration des couleurs personnalisees - DiscordTranscript
# ==============================================================================
# Syntaxe : cle: valeur (hexadecimal, rgb, etc.)
# Les tirets (-) et les underscores (_) sont interchangeables.
# Le prefixe '--' est optionnel.
# ==============================================================================

# -- Couleurs d'accentuation / Boutons Discord --
discord-blurple: #5865F2
discord-blurple-hover: #4752C4
discord-green: #23A55A
discord-green-hover: #1A7F42
discord-red: #F23F43
discord-red-hover: #A1282C
discord-grey: #4E5058
discord-grey-hover: #6D6F78

# -- Arriere-plans --
background-primary: #313338
background-secondary: #2b2d31
background-tertiary: #1e1f22
background-floating: #232428

# -- Textes et Composants UI --
text-white: #FFFFFF
text-normal: #dbdee1
text-muted: #949ba4
discord-text-placeholder: #dbdee1
discord-icon-color: #dbdee1
discord-component-bg: #2B2D31
discord-component-hover: #404249
discord-border-color: #1E1F22
"""


def generate_custom_colors_file(
    target_file: str | Path | os.PathLike, overwrite: bool = False
) -> Path:
    path = Path(target_file)
    if path.exists() and not overwrite:
        raise FileExistsError(
            f"File '{target_file}' already exists. Set overwrite=True to replace it."
        )

    if path.parent:
        path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(_CUSTOM_COLORS_TEMPLATE, encoding="utf-8")
    return path


def parse_custom_colors_file(file_path: str | Path | os.PathLike) -> str:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Custom colors file not found: {file_path}")

    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    css_declarations: list[str] = []
    for line_idx, line in enumerate(lines, start=1):
        cleaned = line.strip()
        if (
            not cleaned
            or cleaned.startswith("#")
            or cleaned.startswith("//")
            or cleaned.startswith("/*")
        ):
            continue

        if ":" not in cleaned:
            raise ValueError(
                f"Invalid syntax at line {line_idx} in '{file_path}': '{line.strip()}'. Expected 'key: value'."
            )

        key, value = cleaned.split(":", 1)
        key = key.strip()
        value = value.strip().rstrip(";").strip()

        if not key:
            raise ValueError(
                f"Invalid key at line {line_idx} in '{file_path}': '{line.strip()}'."
            )
        if not value:
            raise ValueError(
                f"Invalid value for '{key}' at line {line_idx} in '{file_path}'."
            )

        if not key.startswith("--"):
            key = f"--{key}"

        key = key.replace("_", "-")

        css_declarations.append(f"{key}: {value};")

    if not css_declarations:
        return ""

    return "\n            " + "\n            ".join(css_declarations)
