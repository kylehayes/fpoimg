"""Tests for multiple image format support."""
import pytest
import io
from PIL import Image
from fpoimg.generators.formats import EXTENSION_MAP, FORMAT_MIMETYPES
from fpoimg.generators.svg import generate_svg, _rgb_to_hex


class TestExtensionMap:
    def test_png(self):
        assert EXTENSION_MAP["png"] == "PNG"

    def test_jpg(self):
        assert EXTENSION_MAP["jpg"] == "JPEG"

    def test_jpeg(self):
        assert EXTENSION_MAP["jpeg"] == "JPEG"

    def test_webp(self):
        assert EXTENSION_MAP["webp"] == "WEBP"

    def test_svg(self):
        assert EXTENSION_MAP["svg"] == "SVG"


class TestPngRoute:
    def test_default_is_png(self, client):
        resp = client.get("/200x200")
        assert resp.content_type == "image/png"

    def test_explicit_png(self, client):
        resp = client.get("/200x200.png")
        assert resp.status_code == 200
        assert resp.content_type == "image/png"


class TestJpegRoute:
    def test_jpg_extension(self, client):
        resp = client.get("/200x200.jpg")
        assert resp.status_code == 200
        assert resp.content_type == "image/jpeg"
        # JPEG magic bytes
        assert resp.data[:2] == b'\xff\xd8'

    def test_jpeg_extension(self, client):
        resp = client.get("/200x200.jpeg")
        assert resp.status_code == 200
        assert resp.content_type == "image/jpeg"

    def test_jpg_correct_dimensions(self, client):
        resp = client.get("/300x150.jpg")
        img = Image.open(io.BytesIO(resp.data))
        assert img.size == (300, 150)

    def test_jpg_with_caption(self, client):
        resp = client.get("/300x200.jpg/Hello")
        assert resp.status_code == 200
        assert resp.content_type == "image/jpeg"

    def test_jpg_with_gradient(self, client):
        resp = client.get("/300x200.jpg?gradient=sunset")
        assert resp.status_code == 200
        assert resp.content_type == "image/jpeg"


class TestWebpRoute:
    def test_webp_extension(self, client):
        resp = client.get("/200x200.webp")
        assert resp.status_code == 200
        assert resp.content_type == "image/webp"
        # WEBP magic: RIFF....WEBP
        assert resp.data[:4] == b'RIFF'
        assert resp.data[8:12] == b'WEBP'

    def test_webp_correct_dimensions(self, client):
        resp = client.get("/300x150.webp")
        img = Image.open(io.BytesIO(resp.data))
        assert img.size == (300, 150)

    def test_webp_with_caption(self, client):
        resp = client.get("/300x200.webp/Hello")
        assert resp.status_code == 200
        assert resp.content_type == "image/webp"

    def test_webp_square(self, client):
        resp = client.get("/200.webp")
        assert resp.status_code == 200
        assert resp.content_type == "image/webp"


class TestSvgRoute:
    def test_svg_extension(self, client):
        resp = client.get("/200x200.svg")
        assert resp.status_code == 200
        assert "image/svg+xml" in resp.content_type

    def test_svg_contains_dimensions(self, client):
        resp = client.get("/400x300.svg")
        svg = resp.data.decode('utf-8')
        assert 'width="400"' in svg
        assert 'height="300"' in svg
        assert "400\u00D7300" in svg

    def test_svg_with_caption(self, client):
        resp = client.get("/400x300.svg/Hello")
        svg = resp.data.decode('utf-8')
        assert "Hello" in svg

    def test_svg_with_gradient(self, client):
        resp = client.get("/400x300.svg?gradient=sunset")
        svg = resp.data.decode('utf-8')
        assert "linearGradient" in svg

    def test_svg_with_custom_colors(self, client):
        resp = client.get("/200x200.svg?bg_color=FF0000&text_color=00FF00")
        svg = resp.data.decode('utf-8')
        assert "#ff0000" in svg
        assert "#00ff00" in svg

    def test_svg_square(self, client):
        resp = client.get("/200.svg")
        assert resp.status_code == 200
        assert "image/svg+xml" in resp.content_type

    def test_svg_multiline(self, client):
        resp = client.get("/400x300.svg?text=Line+1%5CnLine+2")
        svg = resp.data.decode('utf-8')
        assert "Line 1" in svg
        assert "Line 2" in svg


class TestSvgGenerator:
    def test_returns_bytesio(self):
        buf = generate_svg(200, 100)
        assert hasattr(buf, 'read')

    def test_valid_svg(self):
        buf = generate_svg(200, 100)
        svg = buf.read().decode('utf-8')
        assert svg.startswith('<svg')
        assert '</svg>' in svg

    def test_with_gradient(self):
        buf = generate_svg(200, 100, gradient=((255, 0, 0), (0, 0, 255), 180))
        svg = buf.read().decode('utf-8')
        assert "linearGradient" in svg

    def test_rgb_to_hex(self):
        assert _rgb_to_hex((255, 0, 0)) == "#ff0000"
        assert _rgb_to_hex((0, 255, 0)) == "#00ff00"
        assert _rgb_to_hex((0, 0, 0)) == "#000000"

    def test_escapes_html_in_caption(self):
        buf = generate_svg(200, 100, caption='<script>alert("xss")</script>')
        svg = buf.read().decode('utf-8')
        assert "<script>" not in svg
        assert "&lt;script&gt;" in svg


class TestFormatWithCacheHeaders:
    def test_webp_has_no_cache(self, client):
        resp = client.get("/200x200.webp")
        assert "no-store" in resp.headers.get("Cache-Control", "")

    def test_svg_has_no_cache(self, client):
        resp = client.get("/200x200.svg")
        assert "no-store" in resp.headers.get("Cache-Control", "")

    def test_jpg_has_whats_new(self, client):
        resp = client.get("/200x200.jpg")
        assert "X-FPOImg-New" in resp.headers
