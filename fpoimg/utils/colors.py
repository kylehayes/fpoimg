"""Color parsing and conversion utilities."""
import textwrap


def hex_to_rgb(value):
    """Convert a hex color string to an RGB tuple.

    Supports 3 and 6 digit hex, with or without leading '#'.
    Returns None for empty/whitespace-only strings.
    Raises ValueError for invalid hex strings.

    Algorithm credit: @Jeremy Cantrell on StackOverflow
    http://stackoverflow.com/questions/214359/converting-hex-color-to-rgb-and-vice-versa
    """
    if len(value.strip()) != 0:
        if value[0] == '#':
            value = value[1:]

        len_value = len(value)

        if len_value not in [3, 6]:
            raise ValueError('Incorect a value hex {}'.format(value))

        if len_value == 3:
            value = ''.join(i * 2 for i in value)
        return tuple(int(i, 16) for i in textwrap.wrap(value, 2))
    else:
        return None


def parse_color(value, default):
    """Parse a hex color string, returning default RGB tuple on failure."""
    try:
        if value is None:
            raise ValueError("None value")
        return hex_to_rgb(value)
    except (ValueError, TypeError, AttributeError):
        return hex_to_rgb(default)
