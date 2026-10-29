"""Measurement-ID configuration and consistent coverage of public HTML pages."""
import pytest
from fpoimg.app import create_app


@pytest.mark.parametrize('measurement_id', ['', '396709753', 'G-<script>'])
def test_tracking_is_disabled_without_valid_measurement_id(monkeypatch, measurement_id):
    monkeypatch.setenv('GA4_MEASUREMENT_ID', measurement_id)
    with create_app().test_client() as client:
        assert b'id="fpo-analytics"' not in client.get('/').data
        assert b'UA-1427925-2' not in client.get('/examples').data


def test_configured_tracking_covers_content_pages_but_not_images(monkeypatch):
    monkeypatch.setenv('GA4_MEASUREMENT_ID', 'G-TEST123')
    with create_app().test_client() as client:
        for path in ['/', '/docs', '/colors', '/gradients', '/examples']:
            response = client.get(path)
            assert response.status_code == 200
            assert response.data.count(b'id="fpo-analytics"') == 1
            assert b'data-measurement-id="G-TEST123"' in response.data
        assert b'analytics.js' not in client.get('/30x20.svg').data
        assert client.get('/static/scripts/analytics.js').status_code == 200


def test_production_measurement_id_is_default_and_notice_is_visible(monkeypatch):
    monkeypatch.delenv('GA4_MEASUREMENT_ID', raising=False)
    with create_app().test_client() as client:
        html = client.get('/').data
        assert b'data-measurement-id="G-Q326QZ9K36"' in html
        assert b'Google Analytics uses cookies' in html
