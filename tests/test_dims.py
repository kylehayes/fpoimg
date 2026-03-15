"""Tests for the dims query parameter (hide/show dimension text)."""
from io import BytesIO
from PIL import Image


def test_dims_false_returns_valid_image(client):
    """dims=false returns a valid image with 200 OK."""
    resp = client.get('/400x300?dims=false')
    assert resp.status_code == 200
    img = Image.open(BytesIO(resp.data))
    assert img.size == (400, 300)


def test_dims_false_with_caption(client):
    """dims=false with a caption still returns a valid image."""
    resp = client.get('/400x300/Hello?dims=false')
    assert resp.status_code == 200
    img = Image.open(BytesIO(resp.data))
    assert img.size == (400, 300)


def test_dims_true_explicit(client):
    """dims=true (explicit) behaves the same as default."""
    resp_default = client.get('/400x300')
    resp_true = client.get('/400x300?dims=true')
    assert resp_default.status_code == 200
    assert resp_true.status_code == 200
    # Both should produce identical images
    assert resp_default.data == resp_true.data


def test_dims_absent_shows_dimensions(client):
    """When dims param is absent, dimensions are shown (default)."""
    resp = client.get('/400x300')
    assert resp.status_code == 200
    img = Image.open(BytesIO(resp.data))
    assert img.size == (400, 300)


def test_dims_false_svg(client):
    """dims=false works with SVG format."""
    resp = client.get('/400x300.svg?dims=false')
    assert resp.status_code == 200
    svg_content = resp.data.decode('utf-8')
    assert '<svg' in svg_content
    # Dimension text should NOT appear
    assert '400\u00D7300' not in svg_content


def test_dims_true_svg_has_dimensions(client):
    """Default SVG includes dimension text."""
    resp = client.get('/400x300.svg')
    assert resp.status_code == 200
    svg_content = resp.data.decode('utf-8')
    assert '400\u00D7300' in svg_content


def test_dims_false_with_gradient(client):
    """dims=false works with gradient backgrounds."""
    resp = client.get('/400x300?dims=false&gradient=sunset')
    assert resp.status_code == 200
    img = Image.open(BytesIO(resp.data))
    assert img.size == (400, 300)


def test_dims_false_gradient_and_caption(client):
    """dims=false with gradient and caption returns valid image."""
    resp = client.get('/400x300?dims=false&gradient=sunset&text=Hello')
    assert resp.status_code == 200
    img = Image.open(BytesIO(resp.data))
    assert img.size == (400, 300)


def test_dims_false_svg_with_caption(client):
    """dims=false SVG with caption includes caption but not dimensions."""
    resp = client.get('/400x300.svg?dims=false&text=Hello')
    assert resp.status_code == 200
    svg_content = resp.data.decode('utf-8')
    assert '400\u00D7300' not in svg_content
    assert 'Hello' in svg_content


def test_dims_false_svg_no_text_elements(client):
    """dims=false SVG with no caption has no text elements."""
    resp = client.get('/400x300.svg?dims=false')
    assert resp.status_code == 200
    svg_content = resp.data.decode('utf-8')
    assert '<text' not in svg_content


def test_dims_case_insensitive(client):
    """dims=False and dims=FALSE also work."""
    resp_lower = client.get('/400x300.svg?dims=false')
    resp_mixed = client.get('/400x300.svg?dims=False')
    resp_upper = client.get('/400x300.svg?dims=FALSE')
    for resp in (resp_lower, resp_mixed, resp_upper):
        assert resp.status_code == 200
        assert '400\u00D7300' not in resp.data.decode('utf-8')
