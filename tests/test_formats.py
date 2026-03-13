"""Tests for image serialization formats."""
import pytest
from PIL import Image
from fpoimg.generators.formats import image_to_bytes, FORMAT_MIMETYPES


class TestImageToBytes:
    """image_to_bytes() should serialize PIL images to various formats."""

    def _make_image(self, width=100, height=100):
        return Image.new('RGB', (width, height), (128, 128, 128))

    def test_png_output(self):
        img = self._make_image()
        buf = image_to_bytes(img, "PNG")
        # PNG magic bytes
        assert buf.read(4) == b'\x89PNG'

    def test_jpeg_output(self):
        img = self._make_image()
        buf = image_to_bytes(img, "JPEG")
        # JPEG magic bytes
        assert buf.read(2) == b'\xff\xd8'

    def test_webp_output(self):
        img = self._make_image()
        buf = image_to_bytes(img, "WEBP")
        data = buf.read(12)
        assert data[:4] == b'RIFF'
        assert data[8:12] == b'WEBP'

    def test_buffer_is_seeked_to_start(self):
        img = self._make_image()
        buf = image_to_bytes(img, "PNG")
        assert buf.tell() == 0

    def test_format_mimetypes_complete(self):
        assert "PNG" in FORMAT_MIMETYPES
        assert "JPEG" in FORMAT_MIMETYPES
        assert "WEBP" in FORMAT_MIMETYPES
