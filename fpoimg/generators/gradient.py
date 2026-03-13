"""Gradient background generation for placeholder images."""
import math
from PIL import Image

# Premade gradient presets: name -> (color1, color2, default_angle)
PRESETS = {
    "sunset":       ((255, 94, 58),   (255, 175, 64),  135),
    "ocean":        ((0, 180, 219),   (0, 131, 176),   180),
    "forest":       ((17, 153, 82),   (56, 239, 125),  135),
    "lavender":     ((150, 100, 255), (255, 150, 230),  135),
    "midnight":     ((15, 32, 39),    (44, 83, 100),   180),
    "fire":         ((255, 0, 0),     (255, 165, 0),   135),
    "sky":          ((135, 206, 235), (25, 25, 112),   180),
    "peach":        ((255, 218, 185), (255, 154, 139),  135),
    "mint":         ((162, 255, 204), (64, 224, 208),  135),
    "berry":        ((142, 45, 226),  (74, 0, 224),    135),
    "coral":        ((255, 154, 139), (255, 94, 98),   135),
    "steel":        ((67, 80, 91),    (143, 166, 191), 180),
    "candy":        ((255, 97, 210),  (255, 219, 112), 135),
    "arctic":       ((201, 255, 224), (150, 222, 255), 135),
    "ember":        ((255, 75, 31),   (255, 170, 0),   180),
    "twilight":     ((90, 63, 117),   (44, 19, 56),    180),
    "spring":       ((0, 219, 87),    (255, 235, 59),  135),
    "neon":         ((0, 255, 136),   (2, 163, 255),   135),
    "rose":         ((255, 112, 150), (255, 61, 96),   135),
    "shadow":       ((60, 60, 60),    (30, 30, 30),    180),
}


def create_gradient(width, height, color1, color2, angle=180):
    """Generate a gradient PIL image between two colors.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        color1: Starting RGB tuple
        color2: Ending RGB tuple
        angle: Gradient angle in degrees (0=left-to-right, 90=bottom-to-top,
               180=top-to-bottom, 270=right-to-left)

    Returns:
        PIL.Image.Image: The gradient image in RGB mode
    """
    img = Image.new('RGB', (width, height))
    pixels = img.load()

    # Convert CSS-style gradient angle to a direction vector
    # CSS: 0°=to top, 90°=to right, 180°=to bottom, 270°=to left
    # In image coords, y increases downward, so we negate dy
    rad = math.radians(angle)
    dx = math.sin(rad)
    dy = -math.cos(rad)

    # Project corners onto the gradient axis to find the range
    corners = [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]
    projections = [x * dx + y * dy for x, y in corners]
    min_proj = min(projections)
    max_proj = max(projections)
    proj_range = max_proj - min_proj if max_proj != min_proj else 1.0

    r1, g1, b1 = color1
    r2, g2, b2 = color2
    dr = r2 - r1
    dg = g2 - g1
    db = b2 - b1

    for y in range(height):
        for x in range(width):
            # Project pixel onto gradient axis and normalize to 0-1
            proj = x * dx + y * dy
            t = (proj - min_proj) / proj_range
            t = max(0.0, min(1.0, t))

            r = int(r1 + dr * t)
            g = int(g1 + dg * t)
            b = int(b1 + db * t)
            pixels[x, y] = (r, g, b)

    return img


def parse_gradient_param(gradient_str):
    """Parse a gradient query parameter.

    Args:
        gradient_str: Either a preset name or "color1,color2" hex string

    Returns:
        tuple: (color1, color2, default_angle) or None if invalid/empty
    """
    if not gradient_str:
        return None

    gradient_str = gradient_str.strip().lower()

    # Check presets first
    if gradient_str in PRESETS:
        return PRESETS[gradient_str]

    # Try parsing as "color1,color2"
    parts = gradient_str.split(',')
    if len(parts) == 2:
        try:
            c1 = _parse_hex(parts[0].strip())
            c2 = _parse_hex(parts[1].strip())
            if c1 and c2:
                return (c1, c2, 180)
        except (ValueError, TypeError):
            pass

    return None


def _parse_hex(value):
    """Parse a hex color (with or without #) to an RGB tuple."""
    value = value.lstrip('#')
    if len(value) == 3:
        value = ''.join(c * 2 for c in value)
    if len(value) != 6:
        return None
    try:
        return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return None
