"""Request parameter parsing and validation."""

# Dimension constraints
MIN_DIMENSION = 10
MAX_DIMENSION = 5000

# Default colors
DEFAULT_BG_COLOR = '#C7C7C7'
DEFAULT_TEXT_COLOR = '#8F8F8F'


def clamp_dimension(value):
    """Clamp a dimension value to the allowed range."""
    return min(max(MIN_DIMENSION, value), MAX_DIMENSION)
