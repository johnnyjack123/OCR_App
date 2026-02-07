from flask import Flask
from .extensions import socketio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent          # Ordner, in dem diese Datei liegt

TEMPLATES = BASE_DIR.parent / "templates"           # entspricht ../templates
STATIC    = BASE_DIR.parent / "static"              # entspricht ../static

def create_app():
    app = Flask(__name__,
        template_folder=str(TEMPLATES),
        static_folder=str(STATIC),
    )
    app.config["SECRET_KEY"] = "dev"
    socketio.init_app(app, async_mode="threading", cors_allowed_origins="*")
    return app
