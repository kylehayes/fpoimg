"""Tests for Flask routes and HTTP response behavior."""
import pytest
from PIL import Image
import io


class TestHomePage:
    def test_home_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_home_returns_html(self, client):
        resp = client.get("/")
        assert b"<html" in resp.data.lower() or b"<!doctype" in resp.data.lower()


class TestExamplesPage:
    def test_examples_returns_200(self, client):
        resp = client.get("/examples")
        assert resp.status_code == 200

    def test_examples_returns_html(self, client):
        resp = client.get("/examples")
        assert b"<html" in resp.data.lower() or b"<!doctype" in resp.data.lower()


class TestSquareImage:
    def test_returns_png(self, client):
        resp = client.get("/200")
        assert resp.status_code == 200
        assert resp.content_type == "image/png"

    def test_image_is_square(self, client):
        resp = client.get("/150")
        img = Image.open(io.BytesIO(resp.data))
        assert img.size == (150, 150)

    def test_small_square(self, client):
        resp = client.get("/10")
        img = Image.open(io.BytesIO(resp.data))
        assert img.size == (10, 10)


class TestWidthHeightImage:
    def test_returns_png(self, client):
        resp = client.get("/300x200")
        assert resp.status_code == 200
        assert resp.content_type == "image/png"

    def test_correct_dimensions(self, client):
        resp = client.get("/300x200")
        img = Image.open(io.BytesIO(resp.data))
        assert img.size == (300, 200)

    def test_wide_image(self, client):
        resp = client.get("/800x100")
        img = Image.open(io.BytesIO(resp.data))
        assert img.size == (800, 100)

    def test_tall_image(self, client):
        resp = client.get("/100x600")
        img = Image.open(io.BytesIO(resp.data))
        assert img.size == (100, 600)


class TestDimensionClamping:
    """Dimensions should be clamped to 10-5000."""

    def test_width_clamped_to_minimum(self, client):
        resp = client.get("/1x100")
        img = Image.open(io.BytesIO(resp.data))
        assert img.size[0] == 10

    def test_height_clamped_to_minimum(self, client):
        resp = client.get("/100x1")
        img = Image.open(io.BytesIO(resp.data))
        assert img.size[1] == 10

    def test_width_clamped_to_maximum(self, client):
        resp = client.get("/9999x100")
        img = Image.open(io.BytesIO(resp.data))
        assert img.size[0] == 5000

    def test_height_clamped_to_maximum(self, client):
        resp = client.get("/100x9999")
        img = Image.open(io.BytesIO(resp.data))
        assert img.size[1] == 5000


class TestCaption:
    def test_caption_in_url(self, client):
        resp = client.get("/200x100/Hello%20World")
        assert resp.status_code == 200
        assert resp.content_type == "image/png"
        img = Image.open(io.BytesIO(resp.data))
        assert img.size == (200, 100)

    def test_caption_via_query_param(self, client):
        resp = client.get("/200x100?text=Hello")
        assert resp.status_code == 200
        assert resp.content_type == "image/png"


class TestColors:
    def test_custom_bg_color(self, client):
        resp = client.get("/100x100?bg_color=%23FF0000")
        img = Image.open(io.BytesIO(resp.data))
        pixel = img.getpixel((0, 0))
        assert pixel == (255, 0, 0)

    def test_custom_text_color(self, client):
        resp = client.get("/100x100?text_color=%2300FF00")
        assert resp.status_code == 200

    def test_invalid_bg_color_falls_back(self, client):
        resp = client.get("/100x100?bg_color=ZZZZZZ")
        assert resp.status_code == 200
        img = Image.open(io.BytesIO(resp.data))
        pixel = img.getpixel((0, 0))
        assert pixel == (199, 199, 199)

    def test_invalid_text_color_falls_back(self, client):
        resp = client.get("/100x100?text_color=ZZZZZZ")
        assert resp.status_code == 200


class TestCacheHeaders:
    def test_no_cache_headers(self, client):
        resp = client.get("/200x200")
        cc = resp.headers.get("Cache-Control", "")
        assert "no-store" in cc
        assert "no-cache" in cc
        assert "max-age=0" in cc

    def test_pragma_no_cache(self, client):
        resp = client.get("/200x200")
        assert resp.headers.get("Pragma") == "no-cache"


class TestGradientRoutes:
    def test_preset_gradient(self, client):
        resp = client.get("/200x200?gradient=sunset&text_color=ffffff")
        assert resp.status_code == 200
        assert resp.content_type == "image/png"
        img = Image.open(io.BytesIO(resp.data))
        assert img.size == (200, 200)

    def test_custom_gradient(self, client):
        resp = client.get("/200x200?gradient=FF0000,0000FF")
        assert resp.status_code == 200
        img = Image.open(io.BytesIO(resp.data))
        assert img.size == (200, 200)

    def test_gradient_with_angle(self, client):
        resp = client.get("/200x200?gradient=ocean&gradient_angle=45")
        assert resp.status_code == 200

    def test_invalid_gradient_falls_back_to_solid(self, client):
        resp = client.get("/100x100?gradient=notreal&bg_color=%23FF0000")
        assert resp.status_code == 200
        img = Image.open(io.BytesIO(resp.data))
        # Should fall back to solid bg_color
        pixel = img.getpixel((0, 0))
        assert pixel == (255, 0, 0)

    def test_no_gradient_uses_solid(self, client):
        resp = client.get("/100x100?bg_color=%2300FF00")
        img = Image.open(io.BytesIO(resp.data))
        pixel = img.getpixel((0, 0))
        assert pixel == (0, 255, 0)

    def test_gradient_with_caption(self, client):
        resp = client.get("/300x200/Hello?gradient=mint&text_color=000000")
        assert resp.status_code == 200

    def test_gradients_page(self, client):
        resp = client.get("/gradients")
        assert resp.status_code == 200
        assert b"Gradient" in resp.data


class TestWhatsNewHeader:
    def test_header_present_on_image(self, client):
        resp = client.get("/200x200")
        assert "X-FPOImg-New" in resp.headers
        assert "fpoimg.com" in resp.headers["X-FPOImg-New"]

    def test_header_not_on_html_pages(self, client):
        resp = client.get("/")
        assert "X-FPOImg-New" not in resp.headers

    def test_header_present_with_gradient(self, client):
        resp = client.get("/200x200?gradient=sunset")
        assert "X-FPOImg-New" in resp.headers

    def test_header_can_be_disabled(self, client, monkeypatch):
        monkeypatch.setattr("fpoimg.routes.WHATS_NEW", "")
        resp = client.get("/200x200")
        assert "X-FPOImg-New" not in resp.headers


class TestErrorHandler:
    def test_404_returns_json(self, client):
        resp = client.get("/not/a/valid/route/at/all")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["code"] == 404
        assert "name" in data
        assert "description" in data

    def test_unhandled_exception_returns_500(self, client, monkeypatch):
        """Trigger the generic Exception handler."""
        def explode(*args, **kwargs):
            raise RuntimeError("boom")
        monkeypatch.setattr("fpoimg.routes.generate_image", explode)
        resp = client.get("/200x200")
        assert resp.status_code == 500
        assert b"Server Error" in resp.data
