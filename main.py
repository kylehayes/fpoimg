"""Entry point for the fpoimg application.

For backward compatibility: imports the app factory and creates the app instance.
This keeps deployment configs (e.g. gunicorn main:app) working unchanged.
"""
import os
from fpoimg.app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 3000))
    if port == 3000:
        app.debug = True
    app.run(host='0.0.0.0', port=port)
