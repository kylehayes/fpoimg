"""Text layout and font handling for placeholder images."""
from PIL import ImageFont, ImageDraw, Image


def layout_text(canvas_width, canvas_height, line_spacing, list_of_texts=None):
    """Layout text on a canvas, scaling fonts down if necessary.

    Parameters:
        canvas_width, canvas_height: Dimensions of the canvas
        line_spacing: Space between lines in pixels
        list_of_texts: List of tuples [(text, ttf_path, max_point_size), ...]

    Returns:
        List of tuples: [(text, font, (x, y)), ...]
    """
    if not list_of_texts:
        return []

    target_reduction = 0.8  # reduction factor for oversized text

    # Initialize fonts and calculate dimensions
    fonts, text_sizes, text_heights, text_widths = [], [], [], []

    for text, ttf, max_point in list_of_texts:
        font = ImageFont.truetype(ttf, max_point)
        fonts.append(font)

        _, _, width, height = font.getbbox(text)
        text_sizes.append((width, height))
        text_heights.append(height)
        text_widths.append(width)

    total_text_height = sum(text_heights) + (len(list_of_texts) - 1) * line_spacing
    max_text_width = max(text_widths)

    # Determine the necessary reduction ratio if text doesn't fit the canvas
    height_ratio = (canvas_height * target_reduction) / total_text_height if total_text_height > canvas_height else 1.0
    width_ratio = (canvas_width * target_reduction) / max_text_width if max_text_width > canvas_width else 1.0
    reduction_ratio = min(height_ratio, width_ratio, 1.0)

    # Recalculate font sizes and text dimensions after reduction
    if reduction_ratio < 1.0:
        fonts, text_sizes, text_heights, text_widths = [], [], [], []

        for text, ttf, max_point in list_of_texts:
            new_font_size = max(1, int(reduction_ratio * max_point))
            new_font = ImageFont.truetype(ttf, new_font_size)
            fonts.append(new_font)

            _, _, width, height = new_font.getbbox(text)
            text_sizes.append((width, height))
            text_heights.append(height)
            text_widths.append(width)

        total_text_height = sum(text_heights) + (len(list_of_texts) - 1) * line_spacing

    # Center vertically
    top = (canvas_height - total_text_height) / 2

    # Generate layout positions for each text
    layouts = []
    for idx, (text, ttf, max_point) in enumerate(list_of_texts):
        width, height = text_sizes[idx]
        x_position = (canvas_width - width) / 2
        layouts.append((text, fonts[idx], (x_position, top)))
        top += height + line_spacing

    return layouts


def wrap_text(text, font_path, font_size, max_width):
    """Word-wrap text to fit within a given pixel width.

    Args:
        text: The text string to wrap
        font_path: Path to the TTF font file
        font_size: Font size in points
        max_width: Maximum line width in pixels

    Returns:
        List of strings, one per line
    """
    font = ImageFont.truetype(font_path, font_size)
    # Use a dummy image to measure text
    dummy = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(dummy)

    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width or not current_line:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    del draw
    return lines
