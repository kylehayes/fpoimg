"""Core placeholder image generation."""
from PIL import Image, ImageDraw

from .text import layout_text, wrap_text
from .gradient import create_gradient

# Font paths (relative to working directory)
FONT_BOLD = "ArialBlack.ttf"
FONT_REGULAR = "Arial.ttf"

# Font sizes
DIM_FONT_SIZE = 50
CAPTION_FONT_SIZE = 30


def generate_image(width, height, caption="",
                   bg_color=(100, 100, 100), text_color=(200, 200, 200),
                   gradient=None, gradient_angle=None, show_dims=True):
    """Generate a placeholder PIL image.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        caption: Optional text caption below dimensions
        bg_color: Background color as RGB tuple (used when no gradient)
        text_color: Text color as RGB tuple
        gradient: Optional tuple of (color1, color2, default_angle) for gradient background
        gradient_angle: Optional angle override for gradient direction

    Returns:
        PIL.Image.Image: The generated placeholder image
    """
    if gradient:
        color1, color2, default_angle = gradient
        angle = gradient_angle if gradient_angle is not None else default_angle
        im = create_gradient(width, height, color1, color2, angle)
    else:
        im = Image.new('RGB', (width, height), bg_color)

    # Dimension label (e.g. "300×200")
    dim_text = f"{width}\u00D7{height}"

    draw = ImageDraw.Draw(im)
    text_lines = []
    if show_dims:
        text_lines.append((dim_text, FONT_BOLD, DIM_FONT_SIZE))
    if caption:
        # Support explicit \n line breaks (literal backslash-n from URL)
        caption_parts = caption.replace('\\n', '\n').split('\n')

        for part in caption_parts:
            part = part.strip()
            if not part:
                continue
            # Auto-wrap lines that exceed 80% of image width
            wrapped = wrap_text(part, FONT_REGULAR, CAPTION_FONT_SIZE, int(width * 0.8))
            for line in wrapped:
                text_lines.append((line, FONT_REGULAR, CAPTION_FONT_SIZE))

    if text_lines:
        text_layouts = layout_text(width, height, 10, text_lines)
        for text, font, pos in text_layouts:
            draw.text(pos, text, fill=text_color, font=font)
    del draw

    return im

    return im
