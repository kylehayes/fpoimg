"""SVG placeholder image generation."""
import html
import io


def generate_svg(width, height, caption="",
                 bg_color=(199, 199, 199), text_color=(143, 143, 143),
                 gradient=None, gradient_angle=None, show_dims=True):
    """Generate a placeholder SVG image.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        caption: Optional caption text (supports newlines)
        bg_color: Background RGB tuple
        text_color: Text RGB tuple
        gradient: Optional (color1, color2, default_angle) tuple
        gradient_angle: Optional angle override

    Returns:
        io.BytesIO: Buffer containing the SVG data
    """
    bg_hex = _rgb_to_hex(bg_color)
    text_hex = _rgb_to_hex(text_color)
    dim_text = f"{width}\u00D7{height}"

    defs = ""
    fill = f'fill="{bg_hex}"'

    if gradient:
        c1, c2, default_angle = gradient
        angle = gradient_angle if gradient_angle is not None else default_angle
        c1_hex = _rgb_to_hex(c1)
        c2_hex = _rgb_to_hex(c2)
        defs = _svg_gradient_def(c1_hex, c2_hex, angle)
        fill = 'fill="url(#grad)"'

    # Build text elements
    text_elements = []
    lines = []
    if show_dims:
        lines.append(dim_text)

    if caption:
        caption_parts = caption.replace('\\n', '\n').split('\n')
        for part in caption_parts:
            part = part.strip()
            if part:
                lines.append(part)

    total_lines = len(lines)
    # Approximate line height and starting position
    dim_font_size = min(width * 0.12, height * 0.15, 50)
    caption_font_size = dim_font_size * 0.6
    line_height = dim_font_size * 1.4

    if total_lines > 0:
        total_height = dim_font_size + (total_lines - 1) * line_height
        start_y = (height - total_height) / 2 + dim_font_size * 0.8

        for i, line in enumerate(lines):
            escaped = html.escape(line)
            if show_dims and i == 0:
                # Dimension text — bold
                fs = dim_font_size
                weight = "bold"
            else:
                fs = caption_font_size
                weight = "normal"

            y = start_y + i * line_height
            text_elements.append(
                f'  <text x="{width / 2}" y="{y}" '
                f'font-family="Arial, Helvetica, sans-serif" '
                f'font-size="{fs:.1f}" font-weight="{weight}" '
                f'fill="{text_hex}" text-anchor="middle">'
                f'{escaped}</text>'
            )

    texts_str = "\n".join(text_elements)
    defs_str = f"\n  <defs>{defs}\n  </defs>" if defs else ""

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">{defs_str}
  <rect width="{width}" height="{height}" {fill}/>
{texts_str}
</svg>'''

    buf = io.BytesIO(svg.encode('utf-8'))
    buf.seek(0)
    return buf


def _rgb_to_hex(rgb):
    """Convert RGB tuple to hex string."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def _svg_gradient_def(c1_hex, c2_hex, angle):
    """Generate SVG linear gradient definition."""
    import math
    rad = math.radians(angle)
    # CSS-style: 0=up, 90=right, 180=down
    x1 = 50 - 50 * math.sin(rad)
    y1 = 50 + 50 * math.cos(rad)
    x2 = 50 + 50 * math.sin(rad)
    y2 = 50 - 50 * math.cos(rad)

    return (
        f'\n    <linearGradient id="grad" x1="{x1:.1f}%" y1="{y1:.1f}%" '
        f'x2="{x2:.1f}%" y2="{y2:.1f}%">'
        f'\n      <stop offset="0%" stop-color="{c1_hex}"/>'
        f'\n      <stop offset="100%" stop-color="{c2_hex}"/>'
        f'\n    </linearGradient>'
    )
