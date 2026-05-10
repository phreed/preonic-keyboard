#!/usr/bin/env python3
"""Generate gen/freed-board.json (QMK Configurator format) from src/freed-board.toml."""

import json
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # pip install tomli
    except ImportError:
        print("Error: Python 3.11+ or 'pip install tomli' required", file=sys.stderr)
        sys.exit(1)

ROWS = ("row0", "row1", "row2", "row3", "row4")
KEYS_PER_ROW = 12


def key_to_qmk(entry) -> str:
    """Convert a TOML key entry to its QMK string representation.

    A plain string passes through unchanged.
    An inline table {key="KC_X", mod="MOD"} becomes "MOD(KC_X)".
    """
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        key = entry["key"]
        mod = entry.get("mod")
        if mod:
            return f"{mod}({key})"
        return key
    raise ValueError(f"Unrecognised key entry: {entry!r}")


def layer_to_list(layer: dict) -> list[str]:
    """Flatten a layer's row0–row4 into a single 60-element key list."""
    keys: list[str] = []
    name = layer.get("name", "?")
    for row_name in ROWS:
        row = layer.get(row_name)
        if row is None:
            raise ValueError(f"Layer '{name}' is missing '{row_name}'")
        if len(row) != KEYS_PER_ROW:
            raise ValueError(
                f"Layer '{name}' {row_name} has {len(row)} keys (expected {KEYS_PER_ROW})"
            )
        keys.extend(key_to_qmk(k) for k in row)
    return keys


def main() -> None:
    root = Path(__file__).parent.parent
    toml_path = root / "src" / "freed-board.toml"
    json_path = root / "gen" / "freed-board.json"

    with open(toml_path, "rb") as fh:
        data = tomllib.load(fh)

    meta = data["meta"]
    layers = [layer_to_list(layer) for layer in data["layers"]]

    # QMK wraps the documentation value in literal quotes with a trailing newline.
    # Strip leading/trailing whitespace from the TOML multiline string first.
    documentation = '"' + meta["documentation"].strip() + '"\n'

    output = {
        "version": meta["version"],
        "notes": meta["notes"],
        "documentation": documentation,
        "keyboard": meta["keyboard"],
        "keymap": meta["keymap"],
        "layout": meta["layout"],
        "layers": layers,
        "author": meta["author"],
    }

    with open(json_path, "w") as fh:
        json.dump(output, fh, indent=2)
    print(f"Wrote {json_path}  ({len(layers)} layers)")


if __name__ == "__main__":
    main()
