#!/usr/bin/env python3
"""
Keyboard Layer Visualization Generator

This script reads a QMK keyboard.json file and generates SVG visualizations
for each layer using a template SVG file. Features enhanced keycode parsing
with symbolic representations for modifier combinations and special keys.

Usage:
    python generate_keyboard_layers.py [keyboard.json] [template.svg]
    python generate_keyboard_layers.py --test  # Run parsing tests

Default files:
    - keyboard.json: phreedom.json
    - template.svg: LAYOUT_ortho_5x12-template.svg

Supported QMK Keycodes:
    - Basic keys: KC_A-KC_Z, KC_0-KC_9, KC_F1-KC_F12
    - Modifier combinations: LGUI(KC_S) → ⌘S, LALT(KC_D) → ⌥D, LCTL(KC_F) → ⌃F
    - Shift combinations: LSFT(KC_Q) → ⇧Q, S(KC_Q) → ⇧Q
    - Layer keys: MO(3) → MO3, LT(5,KC_S) → S with "L5/Tap"
    - Modifier taps: LCTL_T(KC_D) → D with "Ctrl/Tap"
    - Special keys: KC_TAB → ⇥, KC_SPC → ␣, KC_ENT → ↵, KC_BSPC → ⌫
    - System keys: QK_BOOT → BOOT, QK_REP → ↻, DB_TOGG → DBG
    - Space Cadet: SC_LSPO → L(, SC_RSPC → R)
    - Transparent: KC_TRNS → ▽

All text content is properly escaped for SVG compatibility, handling
reserved XML characters like &, <, >, ", and '.
"""

import json
import re
import sys
from pathlib import Path

# QMK keycode mappings to human-readable labels
QMK_KEYCODE_MAP = {
    # Basic keys
    "KC_A": "A",
    "KC_B": "B",
    "KC_C": "C",
    "KC_D": "D",
    "KC_E": "E",
    "KC_F": "F",
    "KC_G": "G",
    "KC_H": "H",
    "KC_I": "I",
    "KC_J": "J",
    "KC_K": "K",
    "KC_L": "L",
    "KC_M": "M",
    "KC_N": "N",
    "KC_O": "O",
    "KC_P": "P",
    "KC_Q": "Q",
    "KC_R": "R",
    "KC_S": "S",
    "KC_T": "T",
    "KC_U": "U",
    "KC_V": "V",
    "KC_W": "W",
    "KC_X": "X",
    "KC_Y": "Y",
    "KC_Z": "Z",
    # Numbers
    "KC_1": "1",
    "KC_2": "2",
    "KC_3": "3",
    "KC_4": "4",
    "KC_5": "5",
    "KC_6": "6",
    "KC_7": "7",
    "KC_8": "8",
    "KC_9": "9",
    "KC_0": "0",
    # Function keys
    "KC_F1": "F1",
    "KC_F2": "F2",
    "KC_F3": "F3",
    "KC_F4": "F4",
    "KC_F5": "F5",
    "KC_F6": "F6",
    "KC_F7": "F7",
    "KC_F8": "F8",
    "KC_F9": "F9",
    "KC_F10": "F10",
    "KC_F11": "F11",
    "KC_F12": "F12",
    # Symbols
    "KC_MINS": "-",
    "KC_EQL": "=",
    "KC_LBRC": "[",
    "KC_RBRC": "]",
    "KC_BSLS": "\\",
    "KC_SCLN": ";",
    "KC_QUOT": "'",
    "KC_GRV": "`",
    "KC_COMM": ",",
    "KC_DOT": ".",
    "KC_SLSH": "/",
    "KC_TILD": "~",
    "KC_EXLM": "!",
    "KC_AT": "@",
    "KC_HASH": "#",
    "KC_DLR": "$",
    "KC_PERC": "%",
    "KC_CIRC": "^",
    "KC_AMPR": "&",
    "KC_ASTR": "*",
    "KC_LPRN": "(",
    "KC_RPRN": ")",
    "KC_UNDS": "_",
    "KC_PLUS": "+",
    "KC_LCBR": "{",
    "KC_RCBR": "}",
    "KC_PIPE": "|",
    "KC_COLN": ":",
    "KC_DQUO": '"',
    "KC_LT": "<",
    "KC_GT": ">",
    "KC_QUES": "?",
    # Special keys
    "KC_SPC": "␣",
    "KC_ENT": "↵",
    "KC_BSPC": "⌫",
    "KC_DEL": "⌦",
    "KC_TAB": "⇥",
    "KC_ESC": "⎋",
    "KC_CAPS": "⇪",
    "KC_LSFT": "Shift",
    "KC_RSFT": "Shift",
    "KC_LCTL": "Ctrl",
    "KC_RCTL": "Ctrl",
    "KC_LALT": "Alt",
    "KC_RALT": "Alt",
    "KC_LGUI": "Win",
    "KC_RGUI": "Win",
    # Navigation
    "KC_LEFT": "←",
    "KC_DOWN": "↓",
    "KC_UP": "↑",
    "KC_RGHT": "→",
    "KC_HOME": "Home",
    "KC_END": "End",
    "KC_PGUP": "PgUp",
    "KC_PGDN": "PgDn",
    # Layer keys
    "KC_TRNS": "▽",
    "DF(0)": "L0",
    "DF(1)": "L1",
    "DF(2)": "L2",
    # Audio/Media
    "KC_MUTE": "Mute",
    "KC_VOLD": "Vol-",
    "KC_VOLU": "Vol+",
    "KC_MPLY": "Play",
    "KC_MNXT": "Next",
    "KC_MPRV": "Prev",
    # System
    "QK_BOOT": "Boot",
    "DB_TOGG": "Debug",
    "BL_STEP": "BLight",
    # Mouse
    "KC_MS_U": "M↑",
    "KC_MS_D": "M↓",
    "KC_MS_L": "M←",
    "KC_MS_R": "M→",
    "KC_BTN1": "M1",
    "KC_BTN2": "M2",
    "KC_BTN3": "M3",
}


def escape_svg_text(text: str | None) -> str:
    """Escape reserved XML/SVG characters in text content."""
    if not text:
        return text or ""

    # Handle XML reserved characters
    escaped = text.replace("&", "&amp;")  # Must be first to avoid double-escaping
    escaped = escaped.replace("<", "&lt;")
    escaped = escaped.replace(">", "&gt;")
    escaped = escaped.replace('"', "&quot;")
    escaped = escaped.replace("'", "&apos;")

    return escaped


def test_svg_escaping():
    """Test function to verify SVG character escaping works correctly."""
    test_cases = [
        ("&", "&amp;"),
        ("<", "&lt;"),
        (">", "&gt;"),
        ('"', "&quot;"),
        ("'", "&apos;"),
        ("A&B", "A&amp;B"),
        ("<test>", "&lt;test&gt;"),
        ('Quote: "Hello"', "Quote: &quot;Hello&quot;"),
        ("Normal text", "Normal text"),
        ("", ""),
    ]

    print("Testing SVG character escaping...")
    for input_text, expected in test_cases:
        result = escape_svg_text(input_text)
        if result == expected:
            print(f"✓ '{input_text}' -> '{result}'")
        else:
            print(f"✗ '{input_text}' -> '{result}' (expected '{expected}')")
    print()


def test_keycode_parsing():
    """Test function to verify keycode parsing works correctly."""
    test_cases = [
        ("LGUI(KC_S)", ("⌘S", "Win+S")),
        ("LALT(KC_D)", ("⌥D", "Alt+D")),
        ("LCTL(KC_F)", ("⌃F", "Ctrl+F")),
        ("RCTL(KC_J)", ("⌃J", "Ctrl+J")),
        ("RALT(KC_K)", ("⌥K", "Alt+K")),
        ("RGUI(KC_L)", ("⌘L", "Win+L")),
        ("LSFT(KC_TAB)", ("⇧⇥", "Shift+Tab")),
        ("LSFT(KC_Q)", ("⇧Q", "Shift+Q")),
        ("S(KC_Q)", ("⇧Q", "Shift+Q")),
        ("QK_REP", ("↻", "Repeat")),
        ("QK_BOOT", ("BOOT", "Bootloader")),
        ("SC_LSPO", ("L(", "Space Cadet Left")),
        ("KC_TAB", ("⇥", "KC_TAB")),
        ("KC_SPC", ("␣", "KC_SPC")),
        ("KC_A", ("A", "KC_A")),
        ("KC_TRNS", ("▽", "Transparent")),
        ("MO(3)", ("MO3", "Momentary L3")),
    ]

    print("Testing keycode parsing...")
    for keycode, expected in test_cases:
        result = parse_keycode(keycode)
        if result == expected:
            print(f"✓ '{keycode}' -> {result}")
        else:
            print(f"✗ '{keycode}' -> {result} (expected {expected})")
    print()


def parse_keycode(keycode: str) -> tuple[str, str]:
    """Parse QMK keycode and return human-readable label and description."""
    if not keycode or keycode == "KC_NO":
        return "", ""

    # Handle transparent keys
    if keycode == "KC_TRNS":
        return "▽", "Transparent"

    # Handle modifier keys with other keys like LGUI(KC_S), LALT(KC_D), etc.
    mod_combo_match = re.match(r"([LR](?:GUI|ALT|CTL|SFT))\(KC_([A-Z0-9])\)", keycode)
    if mod_combo_match:
        mod, key = mod_combo_match.groups()
        mod_short = {
            "LGUI": "⌘",  # Command/Windows key
            "RGUI": "⌘",
            "LALT": "⌥",  # Alt/Option key
            "RALT": "⌥",
            "LCTL": "⌃",  # Control key
            "RCTL": "⌃",
            "LSFT": "⇧",  # Shift key
            "RSFT": "⇧",
        }
        symbol = mod_short.get(mod, mod[:4])
        mod_name = {
            "LGUI": "Win",
            "RGUI": "Win",
            "LALT": "Alt",
            "RALT": "Alt",
            "LCTL": "Ctrl",
            "RCTL": "Ctrl",
            "LSFT": "Shift",
            "RSFT": "Shift",
        }
        return f"{symbol}{key}", f"{mod_name.get(mod, mod)}+{key}"

    # Handle shifted keys like S(KC_Q) and LSFT(KC_Q)
    shift_match = re.match(r"(?:L?SFT|S)\(KC_([A-Z0-9])\)", keycode)
    if shift_match:
        key = shift_match.group(1)
        return f"⇧{key}", f"Shift+{key}"

    # Handle layer tap keys like LT(5,KC_S)
    lt_match = re.match(r"LT\((\d+),KC_([A-Z])\)", keycode)
    if lt_match:
        layer, key = lt_match.groups()
        return key.upper(), f"L{layer}/Tap"

    # Handle modifier tap keys like LCTL_T(KC_D)
    mod_tap_match = re.match(r"([LR](?:CTL|ALT|SFT|GUI))_T\(KC_([A-Z])\)", keycode)
    if mod_tap_match:
        mod, key = mod_tap_match.groups()
        mod_short = {
            "LCTL": "Ctrl",
            "RCTL": "Ctrl",
            "LALT": "Alt",
            "RALT": "Alt",
            "LSFT": "Shift",
            "RSFT": "Shift",
            "LGUI": "Win",
            "RGUI": "Win",
        }
        return key.upper(), f"{mod_short.get(mod, mod)}/Tap"

    # Handle momentary layer keys like MO(3)
    mo_match = re.match(r"MO\((\d+)\)", keycode)
    if mo_match:
        layer = mo_match.group(1)
        return f"MO{layer}", f"Momentary L{layer}"

    # Handle layer switching like DF(0)
    df_match = re.match(r"DF\((\d+)\)", keycode)
    if df_match:
        layer = df_match.group(1)
        return f"L{layer}", f"Default L{layer}"

    # Handle special keycodes like QK_REP (repeat)
    if keycode == "QK_REP":
        return "↻", "Repeat"

    # Handle QK_BOOT (bootloader)
    if keycode == "QK_BOOT":
        return "BOOT", "Bootloader"

    # Handle QK_RBT (reboot)
    if keycode == "QK_RBT":
        return "RST", "Reset"

    # Handle EE_CLR (EEPROM clear)
    if keycode == "EE_CLR":
        return "CLR", "EEPROM Clear"

    # Handle DB_TOGG (debug toggle)
    if keycode == "DB_TOGG":
        return "DBG", "Debug Toggle"

    # Handle Space Cadet Shift
    if keycode == "SC_LSPO":
        return "L(", "Space Cadet Left"
    if keycode == "SC_RSPC":
        return "R)", "Space Cadet Right"

    # Handle numpad keys
    numpad_keys = {
        "KC_P0": "0",
        "KC_P1": "1",
        "KC_P2": "2",
        "KC_P3": "3",
        "KC_P4": "4",
        "KC_P5": "5",
        "KC_P6": "6",
        "KC_P7": "7",
        "KC_P8": "8",
        "KC_P9": "9",
        "KC_PDOT": ".",
        "KC_PCMM": ",",
        "KC_PSLS": "/",
        "KC_PAST": "*",
        "KC_PMNS": "-",
        "KC_PPLS": "+",
        "KC_PEQL": "=",
        "KC_PENT": "↵",
    }
    if keycode in numpad_keys:
        return numpad_keys[keycode], f"Numpad {numpad_keys[keycode]}"

    # Handle ANY() keycodes
    any_match = re.match(r"ANY\(([^)]+)\)", keycode)
    if any_match:
        inner = any_match.group(1)
        return inner[:6], f"Any: {inner}"

    # Handle remaining LSFT() keycodes (fallback)
    lsft_match = re.match(r"LSFT\(([^)]+)\)", keycode)
    if lsft_match:
        inner = lsft_match.group(1)
        if inner.startswith("KC_"):
            inner_key = inner[3:]
            # Handle special keys that should show their full name
            if inner_key == "TAB":
                return "⇧⇥", "Shift+Tab"
            return f"⇧{inner_key[:4]}", f"Shift+{inner_key}"
        return f"⇧{inner[:4]}", f"Shift+{inner}"

    # Check standard keycode map
    if keycode in QMK_KEYCODE_MAP:
        label = QMK_KEYCODE_MAP[keycode]
        return label, keycode

    # Handle KC_ prefixed keys that aren't in the map
    if keycode.startswith("KC_"):
        short = keycode[3:]
        # Special handling for common keys
        special_mappings = {
            "TAB": "⇥",
            "SPC": "␣",
            "ENT": "↵",
            "BSPC": "⌫",
            "DEL": "⌦",
            "ESC": "⎋",
            "CAPS": "⇪",
        }
        if short in special_mappings:
            return special_mappings[short], keycode
        return short[:6], keycode

    # Final fallback
    return keycode[:8], keycode


def load_keyboard_json(filepath: str):
    """Load and parse keyboard JSON file."""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: Could not find keyboard file '{filepath}'")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse JSON file '{filepath}': {e}")
        return None


def load_template_svg(filepath: str):
    """Load SVG template file."""
    try:
        with open(filepath, "r") as f:
            template = f.read()
        return template
    except FileNotFoundError:
        print(f"Error: Could not find template file '{filepath}'")
        return None


def generate_layer_svg(
    template: str, keyboard_data: dict[str, any], layer_index: int
) -> str | None:
    """Generate SVG for a specific layer."""
    layers = keyboard_data.get("layers", [])
    if not isinstance(layers, list) or layer_index >= len(layers):
        return None

    layer = layers[layer_index]
    if not isinstance(layer, list):
        return None

    keyboard_name = keyboard_data.get("keymap", "Unknown")
    layout_name = keyboard_data.get("layout", "Unknown")

    # Ensure we have string values
    if not isinstance(keyboard_name, str):
        keyboard_name = "Unknown"
    if not isinstance(layout_name, str):
        layout_name = "Unknown"

    # Create a copy of the template
    svg_content = template

    # Set title and subtitle
    layer_title = f"{keyboard_name} - Layer {layer_index}"
    layer_subtitle = f"Layout: {layout_name}"

    svg_content = svg_content.replace("{{LAYER_TITLE}}", escape_svg_text(layer_title))
    svg_content = svg_content.replace(
        "{{LAYER_SUBTITLE}}", escape_svg_text(layer_subtitle)
    )

    # Fill in key labels
    for i, keycode in enumerate(layer):
        if i >= 60:  # Safety check for 5x12 layout
            break

        # Ensure keycode is a string
        if not isinstance(keycode, str):
            keycode = str(keycode) if keycode is not None else ""

        label, _ = parse_keycode(keycode)

        # Replace placeholders with escaped text
        escaped_label = escape_svg_text(label)
        svg_content = svg_content.replace(f"{{{{KEY_{i}}}}}", escaped_label)
        svg_content = svg_content.replace(f"{{{{SUB_{i}}}}}", "")

    # Clear any remaining placeholders
    for i in range(60):
        svg_content = svg_content.replace(f"{{{{KEY_{i}}}}}", "")
        svg_content = svg_content.replace(f"{{{{SUB_{i}}}}}", "")

    return svg_content


def main():
    """Main function."""
    # Run tests if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_svg_escaping()
        test_keycode_parsing()
        return

    # Parse command line arguments
    if len(sys.argv) > 1:
        keyboard_file = sys.argv[1]
    else:
        keyboard_file = "phreedom.json"

    if len(sys.argv) > 2:
        template_file = sys.argv[2]
    else:
        template_file = "LAYOUT_ortho_5x12-template.svg"

    print(f"Loading keyboard configuration from: {keyboard_file}")
    print(f"Using template: {template_file}")

    # Load files
    keyboard_data = load_keyboard_json(keyboard_file)
    if not keyboard_data:
        sys.exit(1)

    template = load_template_svg(template_file)
    if not template:
        sys.exit(1)

    # Create output directory
    output_dir = Path("keyboard_layers")
    output_dir.mkdir(exist_ok=True)

    # Generate layer SVGs
    keyboard_name = keyboard_data.get("keymap", "keyboard")
    num_layers = len(keyboard_data.get("layers", []))

    print(f"Generating {num_layers} layer visualizations...")

    for layer_index in range(num_layers):
        svg_content = generate_layer_svg(template, keyboard_data, layer_index)
        if svg_content:
            filename = f"{keyboard_name}_layer_{layer_index}.svg"
            filepath = output_dir / filename

            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(svg_content)
                print(f"Generated: {filepath}")
            except IOError as e:
                print(f"Error writing {filepath}: {e}")
                continue

    print(f"\nAll layer visualizations saved to: {output_dir}")
    print("You can open the SVG files in a web browser or vector graphics editor.")
    print(
        "\nNote: Special characters like '&', '<', '>' are properly escaped for SVG compatibility."
    )


if __name__ == "__main__":
    main()
