import pytest
from fpoimg.app import create_app


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Flask test client."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def app_context(app):
    """Application context for testing helpers that don't need a request."""
    with app.app_context():
        yield app
