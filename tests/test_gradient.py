"""Tests for gradient generation and parsing."""
import pytest
from PIL import Image
from fpoimg.generators.gradient import (
    create_gradient, parse_gradient_param, PRESETS, _parse_hex
)


class TestCreateGradient:
    """create_gradient() should produce correctly sized gradient images."""

    def test_returns_pil_image(self):
        img = create_gradient(200, 100, (255, 0, 0), (0, 0, 255))
        assert isinstance(img, Image.Image)

    def test_correct_dimensions(self):
        img = create_gradient(300, 150, (255, 0, 0), (0, 0, 255))
        assert img.size == (300, 150)

    def test_rgb_mode(self):
        img = create_gradient(100, 100, (255, 0, 0), (0, 0, 255))
        assert img.mode == "RGB"

    def test_top_to_bottom_gradient(self):
        """Angle 180 = top-to-bottom. Top should be color1, bottom color2."""
        img = create_gradient(10, 200, (255, 0, 0), (0, 0, 255), angle=180)
        top_pixel = img.getpixel((5, 0))
        bottom_pixel = img.getpixel((5, 199))
        # Top should be more red
        assert top_pixel[0] > bottom_pixel[0]
        # Bottom should be more blue
        assert bottom_pixel[2] > top_pixel[2]

    def test_left_to_right_gradient(self):
        """Angle 90 = to right (CSS-style)."""
        img = create_gradient(200, 10, (255, 0, 0), (0, 0, 255), angle=90)
        left_pixel = img.getpixel((0, 5))
        right_pixel = img.getpixel((199, 5))
        assert left_pixel[0] > right_pixel[0]
        assert right_pixel[2] > left_pixel[2]

    def test_same_colors_produces_solid(self):
        """Same start and end color should produce a solid image."""
        img = create_gradient(100, 100, (128, 128, 128), (128, 128, 128))
        assert img.getpixel((0, 0)) == (128, 128, 128)
        assert img.getpixel((99, 99)) == (128, 128, 128)

    def test_small_image(self):
        img = create_gradient(10, 10, (0, 0, 0), (255, 255, 255))
        assert img.size == (10, 10)

    def test_wide_image(self):
        img = create_gradient(500, 10, (255, 0, 0), (0, 255, 0))
        assert img.size == (500, 10)

    def test_diagonal_gradient(self):
        """135° = to bottom-right. Top-left should be color1, bottom-right color2."""
        img = create_gradient(200, 200, (255, 0, 0), (0, 0, 255), angle=135)
        tl = img.getpixel((0, 0))
        br = img.getpixel((199, 199))
        # Top-left should be more red, bottom-right more blue
        assert tl[0] > br[0]
        assert br[2] > tl[2]


class TestParseGradientParam:
    """parse_gradient_param() should handle presets and custom colors."""

    def test_empty_string_returns_none(self):
        assert parse_gradient_param("") is None

    def test_none_returns_none(self):
        assert parse_gradient_param(None) is None

    def test_preset_name(self):
        result = parse_gradient_param("sunset")
        assert result is not None
        c1, c2, angle = result
        assert c1 == (255, 94, 58)
        assert c2 == (255, 175, 64)

    def test_preset_case_insensitive(self):
        result = parse_gradient_param("SUNSET")
        assert result is not None

    def test_all_presets_valid(self):
        for name in PRESETS:
            result = parse_gradient_param(name)
            assert result is not None
            assert len(result) == 3

    def test_custom_two_colors(self):
        result = parse_gradient_param("FF0000,0000FF")
        assert result is not None
        c1, c2, angle = result
        assert c1 == (255, 0, 0)
        assert c2 == (0, 0, 255)
        assert angle == 180  # default angle for custom

    def test_custom_with_hash(self):
        result = parse_gradient_param("#FF0000,#00FF00")
        assert result is not None
        c1, c2, _ = result
        assert c1 == (255, 0, 0)
        assert c2 == (0, 255, 0)

    def test_custom_three_digit(self):
        result = parse_gradient_param("F00,00F")
        assert result is not None
        c1, c2, _ = result
        assert c1 == (255, 0, 0)
        assert c2 == (0, 0, 255)

    def test_invalid_string_returns_none(self):
        assert parse_gradient_param("notapreset") is None

    def test_single_color_returns_none(self):
        assert parse_gradient_param("FF0000") is None

    def test_invalid_hex_in_custom_returns_none(self):
        assert parse_gradient_param("ZZZZZZ,FFFFFF") is None

    def test_three_colors_returns_none(self):
        assert parse_gradient_param("FF0000,00FF00,0000FF") is None


class TestParseHex:
    """_parse_hex() helper for gradient color parsing."""

    def test_six_digit(self):
        assert _parse_hex("FF0000") == (255, 0, 0)

    def test_three_digit(self):
        assert _parse_hex("F00") == (255, 0, 0)

    def test_with_hash(self):
        assert _parse_hex("#00FF00") == (0, 255, 0)

    def test_invalid_length(self):
        assert _parse_hex("ABCDE") is None

    def test_invalid_chars(self):
        assert _parse_hex("GGGGGG") is None
