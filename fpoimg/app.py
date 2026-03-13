"""Flask application factory."""
import logging
import json
from flask import Flask
from werkzeug.exceptions import HTTPException


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Register blueprints
    from .routes import routes_bp
    app.register_blueprint(routes_bp)

    # Import here to avoid circular imports (test_gallery is at project root)
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from test_gallery import test_gallery_bp
    app.register_blueprint(test_gallery_bp)

    # Error handlers
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        response = e.get_response()
        response.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        })
        response.content_type = "application/json"
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.exception("unhandled exception: %s", str(e))
        return "Server Error", 500

    return app
