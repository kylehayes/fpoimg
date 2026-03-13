"""Core placeholder image generation."""
from PIL import Image, ImageDraw

from .text import layout_text

# Font paths (relative to working directory)
FONT_BOLD = "ArialBlack.ttf"
FONT_REGULAR = "Arial.ttf"

# Font sizes
DIM_FONT_SIZE = 50
CAPTION_FONT_SIZE = 30


def generate_image(width, height, caption="",
                   bg_color=(100, 100, 100), text_color=(200, 200, 200)):
    """Generate a placeholder PIL image.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        caption: Optional text caption below dimensions
        bg_color: Background color as RGB tuple
        text_color: Text color as RGB tuple

    Returns:
        PIL.Image.Image: The generated placeholder image
    """
    im = Image.new('RGB', (width, height), bg_color)

    # Dimension label (e.g. "300×200")
    dim_text = f"{width}\u00D7{height}"

    draw = ImageDraw.Draw(im)
    text_lines = [(dim_text, FONT_BOLD, DIM_FONT_SIZE)]
    if caption:
        text_lines.append((caption, FONT_REGULAR, CAPTION_FONT_SIZE))

    text_layouts = layout_text(width, height, 0, text_lines)
    for text, font, pos in text_layouts:
        draw.text(pos, text, fill=text_color, font=font)
    del draw

    return im
