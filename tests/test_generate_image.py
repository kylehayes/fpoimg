"""Tests for generate_image() — the pure image creation logic."""
import pytest
from PIL import Image
from main import generate_image


class TestGenerateImage:
    """generate_image() creates PIL images without Flask dependencies."""

    def test_returns_pil_image(self):
        img = generate_image(200, 100)
        assert isinstance(img, Image.Image)

    def test_correct_dimensions(self):
        img = generate_image(300, 150)
        assert img.size == (300, 150)

    def test_default_bg_color(self):
        img = generate_image(100, 100)
        pixel = img.getpixel((0, 0))
        assert pixel == (100, 100, 100)

    def test_custom_bg_color(self):
        img = generate_image(100, 100, bg_color=(255, 0, 0))
        pixel = img.getpixel((0, 0))
        assert pixel == (255, 0, 0)

    def test_with_caption(self):
        img = generate_image(400, 200, caption="Test Caption")
        assert img.size == (400, 200)

    def test_rgb_mode(self):
        img = generate_image(100, 100)
        assert img.mode == "RGB"

    def test_one_pixel(self):
        """Minimum possible image."""
        img = generate_image(10, 10)
        assert img.size == (10, 10)

    def test_large_image(self):
        img = generate_image(2000, 2000)
        assert img.size == (2000, 2000)
