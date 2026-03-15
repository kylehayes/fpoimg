"""Color parsing and conversion utilities."""
import textwrap

# All 148 CSS named colors → lowercase name: hex string (without #)
NAMED_COLORS = {
    # Reds
    "indianred": "CD5C5C",
    "lightcoral": "F08080",
    "salmon": "FA8072",
    "darksalmon": "E9967A",
    "lightsalmon": "FFA07A",
    "crimson": "DC143C",
    "red": "FF0000",
    "firebrick": "B22222",
    "darkred": "8B0000",
    # Pinks
    "pink": "FFC0CB",
    "lightpink": "FFB6C1",
    "hotpink": "FF69B4",
    "deeppink": "FF1493",
    "mediumvioletred": "C71585",
    "palevioletred": "DB7093",
    # Oranges
    "coral": "FF7F50",
    "tomato": "FF6347",
    "orangered": "FF4500",
    "darkorange": "FF8C00",
    "orange": "FFA500",
    # Yellows
    "gold": "FFD700",
    "yellow": "FFFF00",
    "lightyellow": "FFFFE0",
    "lemonchiffon": "FFFACD",
    "lightgoldenrodyellow": "FAFAD2",
    "papayawhip": "FFEFD5",
    "moccasin": "FFE4B5",
    "peachpuff": "FFDAB9",
    "palegoldenrod": "EEE8AA",
    "khaki": "F0E68C",
    "darkkhaki": "BDB76B",
    # Purples
    "lavender": "E6E6FA",
    "thistle": "D8BFD8",
    "plum": "DDA0DD",
    "violet": "EE82EE",
    "orchid": "DA70D6",
    "fuchsia": "FF00FF",
    "magenta": "FF00FF",
    "mediumorchid": "BA55D3",
    "mediumpurple": "9370DB",
    "rebeccapurple": "663399",
    "blueviolet": "8A2BE2",
    "darkviolet": "9400D3",
    "darkorchid": "9932CC",
    "darkmagenta": "8B008B",
    "purple": "800080",
    "indigo": "4B0082",
    "slateblue": "6A5ACD",
    "darkslateblue": "483D8B",
    "mediumslateblue": "7B68EE",
    # Greens
    "greenyellow": "ADFF2F",
    "chartreuse": "7FFF00",
    "lawngreen": "7CFC00",
    "lime": "00FF00",
    "limegreen": "32CD32",
    "palegreen": "98FB98",
    "lightgreen": "90EE90",
    "mediumspringgreen": "00FA9A",
    "springgreen": "00FF7F",
    "mediumseagreen": "3CB371",
    "seagreen": "2E8B57",
    "forestgreen": "228B22",
    "green": "008000",
    "darkgreen": "006400",
    "yellowgreen": "9ACD32",
    "olivedrab": "6B8E23",
    "olive": "808000",
    "darkolivegreen": "556B2F",
    "mediumaquamarine": "66CDAA",
    "darkseagreen": "8FBC8F",
    "lightseagreen": "20B2AA",
    "darkcyan": "008B8B",
    "teal": "008080",
    # Blues
    "aqua": "00FFFF",
    "cyan": "00FFFF",
    "lightcyan": "E0FFFF",
    "paleturquoise": "AFEEEE",
    "aquamarine": "7FFFD4",
    "turquoise": "40E0D0",
    "mediumturquoise": "48D1CC",
    "darkturquoise": "00CED1",
    "cadetblue": "5F9EA0",
    "steelblue": "4682B4",
    "lightsteelblue": "B0C4DE",
    "powderblue": "B0E0E6",
    "lightblue": "ADD8E6",
    "skyblue": "87CEEB",
    "lightskyblue": "87CEFA",
    "deepskyblue": "00BFFF",
    "dodgerblue": "1E90FF",
    "cornflowerblue": "6495ED",
    "royalblue": "4169E1",
    "blue": "0000FF",
    "mediumblue": "0000CD",
    "darkblue": "00008B",
    "navy": "000080",
    "midnightblue": "191970",
    # Browns
    "cornsilk": "FFF8DC",
    "blanchedalmond": "FFEBCD",
    "bisque": "FFE4C4",
    "navajowhite": "FFDEAD",
    "wheat": "F5DEB3",
    "burlywood": "DEB887",
    "tan": "D2B48C",
    "rosybrown": "BC8F8F",
    "sandybrown": "F4A460",
    "goldenrod": "DAA520",
    "darkgoldenrod": "B8860B",
    "peru": "CD853F",
    "chocolate": "D2691E",
    "saddlebrown": "8B4513",
    "sienna": "A0522D",
    "brown": "A52A2A",
    "maroon": "800000",
    # Whites
    "white": "FFFFFF",
    "snow": "FFFAFA",
    "honeydew": "F0FFF0",
    "mintcream": "F5FFFA",
    "azure": "F0FFFF",
    "aliceblue": "F0F8FF",
    "ghostwhite": "F8F8FF",
    "whitesmoke": "F5F5F5",
    "seashell": "FFF5EE",
    "beige": "F5F5DC",
    "oldlace": "FDF5E6",
    "floralwhite": "FFFAF0",
    "ivory": "FFFFF0",
    "antiquewhite": "FAEBD7",
    "linen": "FAF0E6",
    "lavenderblush": "FFF0F5",
    "mistyrose": "FFE4E1",
    # Grays
    "gainsboro": "DCDCDC",
    "lightgray": "D3D3D3",
    "lightgrey": "D3D3D3",
    "silver": "C0C0C0",
    "darkgray": "A9A9A9",
    "darkgrey": "A9A9A9",
    "gray": "808080",
    "grey": "808080",
    "dimgray": "696969",
    "dimgrey": "696969",
    "lightslategray": "778899",
    "lightslategrey": "778899",
    "slategray": "708090",
    "slategrey": "708090",
    "darkslategray": "2F4F4F",
    "darkslategrey": "2F4F4F",
    "black": "000000",
}

# Color families for the /colors page
COLOR_FAMILIES = {
    "Reds": [
        "indianred", "lightcoral", "salmon", "darksalmon", "lightsalmon",
        "crimson", "red", "firebrick", "darkred",
    ],
    "Pinks": [
        "pink", "lightpink", "hotpink", "deeppink",
        "mediumvioletred", "palevioletred",
    ],
    "Oranges": [
        "coral", "tomato", "orangered", "darkorange", "orange",
    ],
    "Yellows": [
        "gold", "yellow", "lightyellow", "lemonchiffon",
        "lightgoldenrodyellow", "papayawhip", "moccasin", "peachpuff",
        "palegoldenrod", "khaki", "darkkhaki",
    ],
    "Purples": [
        "lavender", "thistle", "plum", "violet", "orchid", "fuchsia",
        "magenta", "mediumorchid", "mediumpurple", "rebeccapurple",
        "blueviolet", "darkviolet", "darkorchid", "darkmagenta",
        "purple", "indigo", "slateblue", "darkslateblue", "mediumslateblue",
    ],
    "Greens": [
        "greenyellow", "chartreuse", "lawngreen", "lime", "limegreen",
        "palegreen", "lightgreen", "mediumspringgreen", "springgreen",
        "mediumseagreen", "seagreen", "forestgreen", "green", "darkgreen",
        "yellowgreen", "olivedrab", "olive", "darkolivegreen",
        "mediumaquamarine", "darkseagreen", "lightseagreen", "darkcyan", "teal",
    ],
    "Blues": [
        "aqua", "cyan", "lightcyan", "paleturquoise", "aquamarine",
        "turquoise", "mediumturquoise", "darkturquoise", "cadetblue",
        "steelblue", "lightsteelblue", "powderblue", "lightblue", "skyblue",
        "lightskyblue", "deepskyblue", "dodgerblue", "cornflowerblue",
        "royalblue", "blue", "mediumblue", "darkblue", "navy", "midnightblue",
    ],
    "Browns": [
        "cornsilk", "blanchedalmond", "bisque", "navajowhite", "wheat",
        "burlywood", "tan", "rosybrown", "sandybrown", "goldenrod",
        "darkgoldenrod", "peru", "chocolate", "saddlebrown", "sienna",
        "brown", "maroon",
    ],
    "Whites": [
        "white", "snow", "honeydew", "mintcream", "azure", "aliceblue",
        "ghostwhite", "whitesmoke", "seashell", "beige", "oldlace",
        "floralwhite", "ivory", "antiquewhite", "linen", "lavenderblush",
        "mistyrose",
    ],
    "Grays": [
        "gainsboro", "lightgray", "silver", "darkgray", "gray", "dimgray",
        "lightslategray", "slategray", "darkslategray", "black",
    ],
}


def resolve_color(value):
    """Resolve a color string: named color → hex, or pass through.

    Returns the hex string (without #) if it's a named color,
    or the original value unchanged if not.
    """
    if value and value.lower() in NAMED_COLORS:
        return NAMED_COLORS[value.lower()]
    return value


def is_color_value(value):
    """Check if a string looks like a color (named color or valid hex).

    Used for route disambiguation between colors and captions.
    """
    if not value:
        return False
    low = value.lower()
    if low in NAMED_COLORS:
        return True
    # Check valid 3 or 6 digit hex (without #)
    if len(low) in (3, 6):
        try:
            int(low, 16)
            return True
        except ValueError:
            pass
    return False


def hex_to_rgb(value):
    """Convert a hex color string to an RGB tuple.

    Supports 3 and 6 digit hex, with or without leading '#'.
    Also supports CSS named colors.
    Returns None for empty/whitespace-only strings.
    Raises ValueError for invalid hex strings.

    Algorithm credit: @Jeremy Cantrell on StackOverflow
    http://stackoverflow.com/questions/214359/converting-hex-color-to-rgb-and-vice-versa
    """
    if len(value.strip()) != 0:
        # Resolve named colors first
        value = resolve_color(value.strip())

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
    """Parse a color string (hex or named), returning default RGB tuple on failure."""
    try:
        if value is None:
            raise ValueError("None value")
        return hex_to_rgb(value)
    except (ValueError, TypeError, AttributeError):
        return hex_to_rgb(default)
