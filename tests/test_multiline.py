"""Tests for multiline text support."""
import pytest
import io
from PIL import Image
from fpoimg.generators.text import wrap_text
from fpoimg.generators.image import generate_image


class TestWrapText:
    """wrap_text() should split text into lines that fit within a pixel width."""

    def test_short_text_no_wrap(self):
        lines = wrap_text("Hello", "Arial.ttf", 30, 500)
        assert lines == ["Hello"]

    def test_long_text_wraps(self):
        lines = wrap_text("This is a very long caption that should wrap", "Arial.ttf", 30, 200)
        assert len(lines) > 1

    def test_single_long_word_stays_on_one_line(self):
        """A single word wider than max_width should not be split."""
        lines = wrap_text("Supercalifragilisticexpialidocious", "Arial.ttf", 30, 50)
        assert len(lines) == 1

    def test_empty_string(self):
        lines = wrap_text("", "Arial.ttf", 30, 500)
        assert lines == [""]

    def test_preserves_word_order(self):
        text = "one two three four five"
        lines = wrap_text(text, "Arial.ttf", 30, 200)
        rejoined = " ".join(lines)
        assert rejoined == text

    def test_narrow_width_wraps_every_word(self):
        lines = wrap_text("A B C D", "Arial.ttf", 30, 30)
        assert len(lines) >= 2

    def test_respects_max_width(self):
        """All wrapped lines should fit within the max width (with font)."""
        from PIL import ImageFont, ImageDraw, Image
        max_w = 200
        font = ImageFont.truetype("Arial.ttf", 30)
        dummy = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(dummy)
        lines = wrap_text("Here is some text that will need wrapping to fit", "Arial.ttf", 30, max_w)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            assert bbox[2] - bbox[0] <= max_w


class TestMultilineCaption:
    """generate_image() should support multiline captions."""

    def test_explicit_newline(self):
        """\\n in caption should produce multiple lines."""
        img = generate_image(400, 300, caption="Line 1\\nLine 2")
        assert img.size == (400, 300)

    def test_auto_wrap_long_caption(self):
        """Long captions should auto-wrap without errors."""
        img = generate_image(200, 200, caption="This is a very long caption that should auto wrap to multiple lines")
        assert img.size == (200, 200)

    def test_multiple_newlines(self):
        img = generate_image(400, 400, caption="First\\nSecond\\nThird")
        assert img.size == (400, 400)

    def test_newline_and_autowrap_combined(self):
        img = generate_image(200, 300, caption="Short\\nThis line is very long and should wrap automatically")
        assert img.size == (200, 300)

    def test_empty_lines_skipped(self):
        """Empty segments from consecutive \\n should be skipped."""
        img = generate_image(400, 300, caption="Hello\\n\\nWorld")
        assert img.size == (400, 300)

    def test_no_caption_still_works(self):
        img = generate_image(400, 300)
        assert img.size == (400, 300)


class TestMultilineRoutes:
    """Route-level tests for multiline captions."""

    def test_newline_in_query_param(self, client):
        resp = client.get("/300x200?text=Line+1%5CnLine+2")
        assert resp.status_code == 200
        img = Image.open(io.BytesIO(resp.data))
        assert img.size == (300, 200)

    def test_newline_in_url_path(self, client):
        resp = client.get("/300x200/Hello%5CnWorld")
        assert resp.status_code == 200
        img = Image.open(io.BytesIO(resp.data))
        assert img.size == (300, 200)

    def test_long_caption_wraps(self, client):
        resp = client.get("/200x200?text=This+is+a+really+long+caption+that+should+wrap+automatically")
        assert resp.status_code == 200
