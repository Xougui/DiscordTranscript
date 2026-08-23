import os
from pathlib import Path


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
