"""Tests for hex_to_rgb color conversion."""
import pytest
from main import hex_to_rgb


class TestHexToRgb:
    """hex_to_rgb() should handle various hex color formats."""

    # --- Valid inputs ---

    def test_six_digit_with_hash(self):
        assert hex_to_rgb("#FF0000") == (255, 0, 0)

    def test_six_digit_without_hash(self):
        assert hex_to_rgb("00FF00") == (0, 255, 0)

    def test_three_digit_with_hash(self):
        assert hex_to_rgb("#FFF") == (255, 255, 255)

    def test_three_digit_without_hash(self):
        assert hex_to_rgb("000") == (0, 0, 0)

    def test_three_digit_expands_correctly(self):
        # #ABC -> #AABBCC
        assert hex_to_rgb("#ABC") == (170, 187, 204)

    def test_lowercase_hex(self):
        assert hex_to_rgb("#ff8800") == (255, 136, 0)

    def test_mixed_case(self):
        assert hex_to_rgb("#FfAa00") == (255, 170, 0)

    def test_default_bg_color(self):
        assert hex_to_rgb("#C7C7C7") == (199, 199, 199)

    def test_default_text_color(self):
        assert hex_to_rgb("#8F8F8F") == (143, 143, 143)

    # --- Invalid inputs ---

    def test_empty_string_returns_none(self):
        assert hex_to_rgb("") is None

    def test_whitespace_only_returns_none(self):
        assert hex_to_rgb("   ") is None

    def test_wrong_length_raises(self):
        with pytest.raises(ValueError, match="Incorect"):
            hex_to_rgb("#ABCDE")  # 5 chars

    def test_single_char_raises(self):
        with pytest.raises(ValueError, match="Incorect"):
            hex_to_rgb("#A")

    def test_two_chars_raises(self):
        with pytest.raises(ValueError, match="Incorect"):
            hex_to_rgb("#AB")

    def test_four_chars_raises(self):
        with pytest.raises(ValueError, match="Incorect"):
            hex_to_rgb("#ABCD")

    def test_invalid_hex_chars_raises(self):
        with pytest.raises(ValueError):
            hex_to_rgb("#GGGGGG")
