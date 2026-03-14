"""Tests for named color support."""
import pytest
from PIL import Image
import io

from fpoimg.utils.colors import (
    NAMED_COLORS, COLOR_FAMILIES, resolve_color, is_color_value,
    hex_to_rgb, parse_color,
)
from fpoimg.generators.gradient import parse_gradient_param


# ---------------------------------------------------------------------------
# Unit tests: color utilities
# ---------------------------------------------------------------------------

class TestNamedColorMap:
    """The NAMED_COLORS dict should be complete and well-formed."""

    def test_has_148_unique_colors(self):
        # CSS spec has 148 named colors (including grey/gray aliases)
        # We have a few extra aliases (grey variants), so >= 148
        assert len(NAMED_COLORS) >= 148

    def test_all_keys_lowercase(self):
        for name in NAMED_COLORS:
            assert name == name.lower(), f"{name} is not lowercase"

    def test_all_values_are_6_digit_hex(self):
        for name, hex_val in NAMED_COLORS.items():
            assert len(hex_val) == 6, f"{name}: {hex_val} is not 6 digits"
            int(hex_val, 16)  # Should not raise

    def test_common_colors_present(self):
        for name in ["red", "green", "blue", "white", "black", "tomato",
                      "steelblue", "coral", "navy", "gold"]:
            assert name in NAMED_COLORS, f"{name} missing"


class TestColorFamilies:
    """COLOR_FAMILIES should cover all colors and reference valid names."""

    def test_all_family_colors_exist_in_named_colors(self):
        for family, names in COLOR_FAMILIES.items():
            for name in names:
                assert name in NAMED_COLORS, \
                    f"{name} in family '{family}' not in NAMED_COLORS"

    def test_families_are_not_empty(self):
        for family, names in COLOR_FAMILIES.items():
            assert len(names) > 0, f"Family '{family}' is empty"


class TestResolveColor:
    def test_named_color(self):
        assert resolve_color("tomato") == "FF6347"

    def test_named_color_case_insensitive(self):
        assert resolve_color("Tomato") == "FF6347"
        assert resolve_color("TOMATO") == "FF6347"

    def test_hex_passthrough(self):
        assert resolve_color("FF0000") == "FF0000"

    def test_none_passthrough(self):
        assert resolve_color(None) is None

    def test_unknown_passthrough(self):
        assert resolve_color("notacolor") == "notacolor"


class TestIsColorValue:
    def test_named_color(self):
        assert is_color_value("tomato") is True

    def test_named_color_case_insensitive(self):
        assert is_color_value("Tomato") is True

    def test_valid_6_digit_hex(self):
        assert is_color_value("FF0000") is True

    def test_valid_3_digit_hex(self):
        assert is_color_value("F00") is True

    def test_caption_text(self):
        assert is_color_value("Hello World") is False

    def test_empty_string(self):
        assert is_color_value("") is False

    def test_none(self):
        assert is_color_value(None) is False

    def test_invalid_hex_length(self):
        assert is_color_value("FF00") is False

    def test_non_hex_chars(self):
        assert is_color_value("ZZZZZZ") is False


class TestHexToRgbWithNames:
    def test_named_color(self):
        assert hex_to_rgb("tomato") == (255, 99, 71)

    def test_named_color_case_insensitive(self):
        assert hex_to_rgb("SteelBlue") == (70, 130, 180)

    def test_white(self):
        assert hex_to_rgb("white") == (255, 255, 255)

    def test_black(self):
        assert hex_to_rgb("black") == (0, 0, 0)


class TestParseColorWithNames:
    def test_named_color(self):
        assert parse_color("tomato", "#000000") == (255, 99, 71)

    def test_named_color_case_insensitive(self):
        assert parse_color("CORAL", "#000000") == (255, 127, 80)

    def test_unknown_name_falls_back(self):
        assert parse_color("notacolor", "#C7C7C7") == (199, 199, 199)

    def test_hex_still_works(self):
        assert parse_color("#FF0000", "#000000") == (255, 0, 0)

    def test_named_color_as_default(self):
        # Default can also be a named color (though our code passes hex defaults)
        assert parse_color(None, "FF0000") == (255, 0, 0)


# ---------------------------------------------------------------------------
# Unit tests: gradient with named colors
# ---------------------------------------------------------------------------

class TestGradientNamedColors:
    def test_custom_gradient_with_named_colors(self):
        result = parse_gradient_param("tomato,steelblue")
        assert result is not None
        c1, c2, angle = result
        assert c1 == (255, 99, 71)
        assert c2 == (70, 130, 180)

    def test_custom_gradient_mixed_hex_and_name(self):
        result = parse_gradient_param("FF0000,navy")
        assert result is not None
        c1, c2, _ = result
        assert c1 == (255, 0, 0)
        assert c2 == (0, 0, 128)

    def test_custom_gradient_name_and_hex(self):
        result = parse_gradient_param("coral,0000FF")
        assert result is not None
        c1, c2, _ = result
        assert c1 == (255, 127, 80)
        assert c2 == (0, 0, 255)

    def test_invalid_names_return_none(self):
        result = parse_gradient_param("notacolor,alsonotacolor")
        assert result is None


# ---------------------------------------------------------------------------
# Route tests
# ---------------------------------------------------------------------------

class TestNamedColorRoutes:
    """Routes using named colors in URL path and query params."""

    def test_bg_color_query_param(self, client):
        resp = client.get("/100x100?bg_color=tomato")
        assert resp.status_code == 200
        img = Image.open(io.BytesIO(resp.data))
        pixel = img.getpixel((0, 0))
        assert pixel == (255, 99, 71)

    def test_text_color_query_param(self, client):
        resp = client.get("/100x100?text_color=navy")
        assert resp.status_code == 200

    def test_path_bg_color_width_height(self, client):
        resp = client.get("/100x100/tomato")
        assert resp.status_code == 200
        img = Image.open(io.BytesIO(resp.data))
        pixel = img.getpixel((0, 0))
        assert pixel == (255, 99, 71)

    def test_path_bg_and_text_width_height(self, client):
        resp = client.get("/100x100/tomato/white")
        assert resp.status_code == 200
        img = Image.open(io.BytesIO(resp.data))
        pixel = img.getpixel((0, 0))
        assert pixel == (255, 99, 71)

    def test_path_bg_color_square(self, client):
        resp = client.get("/100/steelblue")
        assert resp.status_code == 200
        img = Image.open(io.BytesIO(resp.data))
        pixel = img.getpixel((0, 0))
        assert pixel == (70, 130, 180)

    def test_path_bg_and_text_square(self, client):
        resp = client.get("/100/coral/white")
        assert resp.status_code == 200
        img = Image.open(io.BytesIO(resp.data))
        pixel = img.getpixel((0, 0))
        assert pixel == (255, 127, 80)

    def test_path_hex_color_width_height(self, client):
        resp = client.get("/100x100/FF0000")
        assert resp.status_code == 200
        img = Image.open(io.BytesIO(resp.data))
        pixel = img.getpixel((0, 0))
        assert pixel == (255, 0, 0)

    def test_path_hex_colors_width_height(self, client):
        resp = client.get("/100x100/FF0000/00FF00")
        assert resp.status_code == 200
        img = Image.open(io.BytesIO(resp.data))
        pixel = img.getpixel((0, 0))
        assert pixel == (255, 0, 0)

    def test_caption_still_works(self, client):
        """Non-color strings in the path should still be treated as captions."""
        resp = client.get("/200x100/Hello%20World")
        assert resp.status_code == 200
        img = Image.open(io.BytesIO(resp.data))
        assert img.size == (200, 100)

    def test_gradient_with_named_colors(self, client):
        resp = client.get("/200x200?gradient=tomato,steelblue")
        assert resp.status_code == 200
        img = Image.open(io.BytesIO(resp.data))
        assert img.size == (200, 200)


class TestColorsPage:
    def test_colors_page_returns_200(self, client):
        resp = client.get("/colors")
        assert resp.status_code == 200

    def test_colors_page_has_html(self, client):
        resp = client.get("/colors")
        assert b"Named Colors" in resp.data

    def test_colors_page_lists_color_names(self, client):
        resp = client.get("/colors")
        assert b"tomato" in resp.data
        assert b"steelblue" in resp.data

    def test_colors_page_has_families(self, client):
        resp = client.get("/colors")
        assert b"Reds" in resp.data
        assert b"Blues" in resp.data
        assert b"Greens" in resp.data
