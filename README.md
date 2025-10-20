# FreedBoard Keyboard Project

This project contains the FreedBoard keyboard layout - a modern keyboard implementation with advanced modifier handling and multiple layers for ortholinear keyboards. The project includes tools for generating visual representations of keyboard layouts from QMK JSON configuration files.

## Quick Start with Pixi

This project uses [pixi](https://pixi.sh) for dependency management and task automation. First, install pixi if you haven't already:

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

Then run any of the available tasks:

```bash
# Generate SVG layer visualizations
pixi run generate-svg

# Build PDF documentation
pixi run build-pdf  

# Lint the keyboard configuration
pixi run lint-config

# Compile firmware
pixi run compile-firmware

# Flash keyboard (requires connected keyboard)
pixi run flash-keyboard

# Build all outputs (SVG + PDF)
pixi run build-all

# Full workflow (lint + build + compile)
pixi run workflow

# Clean generated files
pixi run clean
```

## Available Tasks

| Task | Description |
|------|-------------|
| `generate-svg` | Generate SVG layer files from phreedom.json |
| `build-pdf` | Build PDF documentation from FreedBoard.adoc |
| `lint-config` | Lint the phreedom.json configuration using QMK |
| `compile-firmware` | Compile firmware using QMK |
| `flash-keyboard` | Flash the keyboard with compiled firmware |
| `build-all` | Generate SVGs and build PDF |
| `workflow` | Complete workflow: lint → build → compile |
| `clean` | Remove all generated files |

## Project Structure

The project consists of:
- **SVG Template**: `LAYOUT_ortho_5x12-template.svg` - Base template for the Preonic keyboard layout
- **Python Generator**: `generate_keyboard_layers.py` - Script to generate layer visualizations
- **Generated Layers**: `keyboard_layers/` - Directory containing generated SVG files

## Files

### Core Files
- `LAYOUT_ortho_5x12-template.svg` - SVG template for 5×12 ortholinear layout
- `generate_keyboard_layers.py` - Python script for generating visualizations
- `phreedom.json` - Example QMK keyboard configuration
- `FreedBoard.adoc` - Documentation of the keyboard layout concept

### Generated Files
- `keyboard_layers/phreedom_layer_*.svg` - Individual layer visualizations
- `CONVERSION_SUMMARY.md` - Process documentation
- `README_VISUALIZATION.md` - This file

## Manual Usage (without pixi)

If you prefer not to use pixi, you can run commands manually:

### Prerequisites
- Python 3.8 or higher
- QMK CLI (`pip install qmk`)
- Asciidoctor and asciidoctor-pdf

### Generate Visualizations

```bash
# Using default files (phreedom.json + LAYOUT_ortho_5x12-template.svg)
python scripts/generate_keyboard_layers.py

# Using custom files  
python scripts/generate_keyboard_layers.py my_keyboard.json my_template.svg
```

### Build Documentation
```bash
asciidoctor-pdf FreedBoard.adoc -o FreedBoard.pdf
```

### QMK Commands
```bash
# Lint configuration
qmk lint phreedom.json

# Compile firmware
qmk compile phreedom.json

# Flash keyboard
qmk flash phreedom.json
```

### View Results
Open any generated SVG file in:
- Web browser (Chrome, Firefox, Safari, etc.)
- Vector graphics editor (Inkscape, Adobe Illustrator, etc.)
- SVG viewer application

## SVG Template Format

The template uses placeholder syntax for dynamic content:

### Title Placeholders
- `{{LAYER_TITLE}}` - Main title (e.g., "phreedom - Layer 0")
- `{{LAYER_SUBTITLE}}` - Subtitle (e.g., "Layout: LAYOUT_ortho_5x12")

### Key Placeholders
For each key position (0-59 for 5×12 layout):
- `{{KEY_N}}` - Primary key label
- `{{SUB_N}}` - Secondary key label (smaller text)

Where N is the key index (0-59).

### Template Structure
```xml
<!-- Title -->
<text>{{LAYER_TITLE}}</text>
<text>{{LAYER_SUBTITLE}}</text>

<!-- Key example -->
<rect class="key" id="key-0"/>
<text class="key-text">{{KEY_0}}</text>
<text class="key-secondary">{{SUB_0}}</text>
```

## Key Index Mapping (5×12 Layout)

```
Row 0:  0  1  2  3  4  5  6  7  8  9 10 11
Row 1: 12 13 14 15 16 17 18 19 20 21 22 23
Row 2: 24 25 26 27 28 29 30 31 32 33 34 35
Row 3: 36 37 38 39 40 41 42 43 44 45 46 47
Row 4: 48 49 50 51 52 53 54 55 56 57 58 59
```

## QMK Keycode Support

The generator supports common QMK keycodes:

### Basic Keys
- `KC_A` → `A`
- `KC_1` → `1`
- `KC_F1` → `F1`

### Special Keys
- `KC_SPC` → `Space`
- `KC_ENT` → `Enter`
- `KC_BSPC` → `Backsp`
- `KC_TRNS` → `▽` (transparent)

### Modifiers
- `KC_LSFT` → `Shift`
- `KC_LCTL` → `Ctrl`
- `KC_LALT` → `Alt`
- `KC_LGUI` → `Win`

### Advanced Keycodes
- `LT(5,KC_S)` → `S` with description "L5/Tap"
- `LCTL_T(KC_D)` → `D` with description "Ctrl/Tap"
- `MO(3)` → `MO3` with description "Momentary L3"
- `DF(1)` → `L1` with description "Default L1"
- `S(KC_Q)` → `Q` with description "Shift+Q"

### Navigation
- `KC_LEFT` → `←`
- `KC_UP` → `↑`
- `KC_DOWN` → `↓`
- `KC_RGHT` → `→`

## Keyboard JSON Format

The script expects QMK Configurator JSON format:

```json
{
  "version": 1,
  "notes": "Description",
  "keyboard": "preonic/rev3",
  "keymap": "my_keymap",
  "layout": "LAYOUT_ortho_5x12",
  "layers": [
    [
      "KC_1", "KC_Q", "KC_W", "KC_E", "KC_R", "KC_T",
      "MO(3)", "KC_LGUI", "KC_Y", "KC_U", "KC_I", "KC_O",
      ...
    ],
    [
      // Layer 1 keycodes...
    ]
  ]
}
```

## Customization

### Creating New Templates

1. Design SVG layout with appropriate dimensions
2. Add CSS styling for `.key`, `.key-text`, `.key-secondary` classes
3. Include placeholders for titles and keys
4. Ensure proper key indexing (0-based)

### Extending Keycode Support

Edit `QMK_KEYCODE_MAP` in `generate_keyboard_layers.py`:

```python
QMK_KEYCODE_MAP = {
    "KC_MYCUSTOM": "Custom",
    # ... existing mappings
}
```

Or modify the `parse_keycode()` function for complex parsing.

### Styling

Modify CSS in the SVG template:

```css
.key {
    fill: #your-color;
    stroke: #border-color;
    /* ... */
}
```

## FreedBoard Integration

This visualization system was created specifically for the FreedBoard keyboard layout:

- **5×12 ortholinear layout** (60 keys)
- **Multiple layers** with specific functions
- **Advanced modifier handling** with home-row modifiers
- **QMK firmware compatibility**

See `FreedBoard.adoc` for detailed layout documentation.

## Output Examples

Generated files follow the naming pattern:
- `{keymap}_layer_0.svg` - Base layer
- `{keymap}_layer_1.svg` - Layer 1
- `{keymap}_layer_N.svg` - Layer N

Each file contains:
- Clean visual representation of the keyboard
- Key labels based on QMK keycodes
- Layer identification in title
- Scalable vector graphics (SVG) format

## Troubleshooting

### Common Issues

**"Could not find keyboard file"**
- Verify the JSON file exists
- Check file permissions
- Use absolute path if needed

**"Could not parse JSON file"**
- Validate JSON syntax
- Ensure proper QMK format
- Check for trailing commas

**Missing key labels**
- Unknown keycodes display as truncated text
- Add mappings to `QMK_KEYCODE_MAP`
- Check keycode spelling

**Template not found**
- Verify SVG template file exists
- Ensure proper placeholder format
- Check file permissions

### Debugging

Enable verbose output by modifying the script:

```python
# Add debug prints
print(f"Processing keycode: {keycode}")
print(f"Parsed as: {label}")
```

## Contributing

To contribute improvements:

1. Test with various keyboard configurations
2. Add support for additional layouts
3. Enhance keycode parsing
4. Improve visual styling
5. Add error handling

## License

This visualization system is part of the FreedBoard keyboard project and follows the same licensing terms as the main project.