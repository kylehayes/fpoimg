import pytest
from main import app


@pytest.fixture
def client():
    """Flask test client with testing mode enabled."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def app_context():
    """Application context for testing helpers that don't need a request."""
    with app.app_context():
        yield app
