"""Tests for color utility functions."""
import pytest
from fpoimg.utils.colors import parse_color


class TestParseColor:
    """parse_color() should return RGB tuples with graceful fallback."""

    def test_valid_hex(self):
        assert parse_color("#FF0000", "#000000") == (255, 0, 0)

    def test_invalid_hex_returns_default(self):
        assert parse_color("ZZZZZZ", "#C7C7C7") == (199, 199, 199)

    def test_none_returns_default(self):
        assert parse_color(None, "#C7C7C7") == (199, 199, 199)

    def test_empty_string_returns_none_from_hex(self):
        # Empty string -> hex_to_rgb returns None, not the default
        # This matches the original behavior
        result = parse_color("", "#C7C7C7")
        assert result is None

    def test_three_digit_hex(self):
        assert parse_color("#F00", "#000000") == (255, 0, 0)
