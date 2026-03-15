# FPOimg

A simple, flexible placeholder image generator service for developers and designers.

## Overview

FPOimg (For Placement Only Image) is a lightweight Flask-based web service that dynamically generates placeholder images on demand. Perfect for mockups, wireframes, and prototypes where you need consistently sized visual elements.

## Features

- **Simple URL-based API**: Generate images using straightforward URL patterns
- **Custom Dimensions**: Specify exact width and height for your placeholders
- **Gradient Backgrounds**: 20 premade gradient presets or custom two-color gradients
- **Text Overlays**: Add dimension information and custom captions
- **Color Customization**: Control both background and text colors
- **Responsive Design**: Works with images from 10px to 5000px in size
- **Lightweight**: No external analytics dependencies, just simple logging

## Usage

### Basic Examples

```
/300            → 300×300 square image
/800x600        → 800×600 rectangular image
/500x200/Hello  → 500×200 image with "Hello" caption
```

### Multiline Text

Captions support explicit line breaks and automatic word wrapping:

```
/400x300?text=Line+1\nLine+2                    → Explicit line break
/400x300/Title\nSubtitle                         → Line break in URL path
/200x200?text=Long+caption+that+wraps+automatically → Auto-wraps to fit
```

Combine both — explicit breaks with auto-wrap on each segment:
```
/300x400?text=Heading\nThis+is+a+longer+description+that+will+wrap+automatically
```

### Gradient Backgrounds

Add beautiful gradients with a single parameter:

```
/800x600?gradient=sunset                          → Premade sunset gradient
/800x600?gradient=ocean&text_color=ffffff          → Ocean gradient with white text
/400x300?gradient=FF5733,3357FF                   → Custom two-color gradient
/400x300?gradient=FF5733,3357FF&gradient_angle=45 → Custom gradient at 45°
```

#### Available Presets

| Preset | Colors | Preset | Colors |
|--------|--------|--------|--------|
| `sunset` | 🟧 orange to gold | `ocean` | 🔵 teal to blue |
| `forest` | 🟢 green to mint | `lavender` | 🟣 purple to pink |
| `midnight` | ⬛ dark teal | `fire` | 🔴 red to orange |
| `sky` | 🔵 light blue to navy | `peach` | 🟠 peach to salmon |
| `mint` | 🟢 mint to teal | `berry` | 🟣 purple to violet |
| `coral` | 🟠 salmon to red | `steel` | ⬛ dark gray to light |
| `candy` | 🩷 pink to yellow | `arctic` | 🔵 mint to blue |
| `ember` | 🔴 orange-red to gold | `twilight` | 🟣 purple to dark |
| `spring` | 🟢 green to yellow | `neon` | 🟢 green to blue |
| `rose` | 🩷 pink to red | `shadow` | ⬛ gray to dark |

Browse all presets with live previews at [fpoimg.com/gradients](https://fpoimg.com/gradients).

### Named Colors

Use any of the 148 CSS named colors instead of hex codes — in the URL path or as query parameters:

```
/400x300/tomato/white             → Tomato background with white text
/300/steelblue                    → 300×300 square with steelblue background
/800x600?bg_color=coral&text_color=navy  → Coral background, navy text
/500x300?gradient=tomato,steelblue       → Gradient using named colors
```

Named colors work everywhere hex codes work: `bg_color`, `text_color`, gradient custom colors, and URL path colors.

Browse all 148 colors with live swatches at [fpoimg.com/colors](https://fpoimg.com/colors).

### Hide Dimensions

Remove the dimension label for a clean placeholder background:

```
/800x600?dims=false                              → No dimension text
/800x600/Hello?dims=false                        → Caption only, no "800×600"
/800x600?dims=false&gradient=sunset               → Clean gradient, no text
/800x600?dims=false&gradient=ocean&text=Hero      → Gradient with caption only
```

### URL Path Colors

Set background and text colors directly in the URL path (hex or named):

```
/400x300/FF5733/FFFFFF            → Orange background, white text (hex)
/400x300/tomato/white             → Same thing with named colors
/300/steelblue                    → Square with just a background color
```

### URL Parameters

Customize your images with query parameters:

```
/500x300?bg_color=FF5733&text_color=FFFFFF     → Orange background with white text
/400x200?text=Custom+Caption                   → Image with custom caption text
/800x400?gradient=sunset&text_color=ffffff      → Sunset gradient with white text
```

### Parameter Reference

| Parameter | Description | Default |
|-----------|-------------|---------|
| `bg_color` | Background color (hex or [named color](https://fpoimg.com/colors)) | `#C7C7C7` |
| `text_color` | Text color (hex or [named color](https://fpoimg.com/colors)) | `#8F8F8F` |
| `text` | Caption text (supports `\n` for line breaks, auto-wraps long text) | None |
| `gradient` | Gradient preset name or `color1,color2` hex | None |
| `gradient_angle` | Gradient direction in degrees (CSS-style: 0°=up, 90°=right, 180°=down) | Preset default or `180` |
| `dims` | Show dimension text (`true` or `false`) | `true` |

> **Note:** When `gradient` is set, `bg_color` is ignored. Omit `gradient` for a solid color background.

## Pages

| URL | Description |
|-----|-------------|
| `/` | Homepage with interactive image generator |
| `/gradients` | Gradient picker with all presets + custom builder |
| `/colors` | Named color reference with swatches grouped by family |
| `/examples` | Example use cases |
| `/test` | Test gallery with randomized images |

## Self-Hosting

### Requirements

- Python 3.11+
- Flask
- Pillow (PIL Fork)
- Required fonts: Arial.ttf, ArialBlack.ttf

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/kylehayes/fpoimg.git
   cd fpoimg
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server
   ```bash
   python main.py
   ```

   The server starts on `http://localhost:3000` by default. Set the `PORT` environment variable to change it.

### Running Tests

```bash
pytest tests/ -v --cov=fpoimg --cov-report=term-missing
```

## Project Structure

```
fpoimg/
├── app.py              — Flask app factory
├── routes.py           — Route definitions
├── generators/
│   ├── image.py        — Core image generation
│   ├── gradient.py     — Gradient backgrounds + presets
│   ├── text.py         — Text layout and font scaling
│   └── formats.py      — Image serialization (PNG)
└── utils/
    ├── colors.py       — Color parsing utilities
    └── params.py       — Dimension clamping + constants
```

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

FPOimg has been providing free placeholder images for over 12 years. Help keep it running:

- [Buy Me a Coffee](https://buymeacoffee.com/kylehayes)
- [GitHub Sponsors](https://github.com/sponsors/kylehayes)
