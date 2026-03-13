"""Tests for layout_text() text positioning logic."""
import pytest
from fpoimg.generators.text import layout_text


class TestLayoutText:
    """layout_text() should position and scale text within canvas bounds."""

    def test_empty_list_returns_empty(self):
        result = layout_text(400, 300, 10, [])
        assert result == []

    def test_none_returns_empty(self):
        result = layout_text(400, 300, 10, None)
        assert result == []

    def test_default_returns_empty(self):
        result = layout_text(400, 300, 10)
        assert result == []

    def test_single_text_returns_one_layout(self):
        result = layout_text(400, 300, 10, [("Hello", "Arial.ttf", 30)])
        assert len(result) == 1
        text, font, (x, y) = result[0]
        assert text == "Hello"

    def test_single_text_is_centered_horizontally(self):
        result = layout_text(400, 300, 10, [("Test", "Arial.ttf", 30)])
        _, _, (x, _) = result[0]
        assert 0 < x < 400

    def test_single_text_is_centered_vertically(self):
        result = layout_text(400, 300, 10, [("Test", "Arial.ttf", 30)])
        _, _, (_, y) = result[0]
        assert 0 < y < 300

    def test_multiple_texts_return_correct_count(self):
        texts = [
            ("Line 1", "Arial.ttf", 30),
            ("Line 2", "Arial.ttf", 20),
        ]
        result = layout_text(400, 300, 10, texts)
        assert len(result) == 2

    def test_multiple_texts_ordered_top_to_bottom(self):
        texts = [
            ("First", "Arial.ttf", 30),
            ("Second", "Arial.ttf", 20),
        ]
        result = layout_text(400, 300, 10, texts)
        _, _, (_, y1) = result[0]
        _, _, (_, y2) = result[1]
        assert y1 < y2

    def test_text_scales_down_when_too_wide(self):
        result_narrow = layout_text(50, 300, 0, [("Wide text here", "Arial.ttf", 40)])
        result_wide = layout_text(2000, 300, 0, [("Wide text here", "Arial.ttf", 40)])
        narrow_font = result_narrow[0][1]
        wide_font = result_wide[0][1]
        assert narrow_font.size <= wide_font.size

    def test_text_scales_down_when_too_tall(self):
        texts = [
            ("Line 1", "ArialBlack.ttf", 50),
            ("Line 2", "Arial.ttf", 30),
            ("Line 3", "Arial.ttf", 30),
        ]
        result = layout_text(400, 30, 10, texts)
        assert len(result) == 3
        for _, font, _ in result:
            assert font.size < 50

    def test_preserves_text_content(self):
        texts = [
            ("200\u00D7100", "ArialBlack.ttf", 50),
            ("caption here", "Arial.ttf", 30),
        ]
        result = layout_text(400, 300, 0, texts)
        assert result[0][0] == "200\u00D7100"
        assert result[1][0] == "caption here"

    def test_minimum_font_size_is_one(self):
        result = layout_text(1, 1, 0, [("Hello World This Is Long", "Arial.ttf", 100)])
        _, font, _ = result[0]
        assert font.size >= 1
