from flask import Flask
from .extensions import socketio
from pathlib import Path
from utils.file_handler import load_file
from utils.logger import logger
from utils.outsourced_functions import set_cookie_key

BASE_DIR = Path(__file__).resolve().parent          # Ordner, in dem diese Datei liegt

TEMPLATES = BASE_DIR.parent / "templates"           # entspricht ../templates
STATIC    = BASE_DIR.parent / "static"              # entspricht ../static

def create_app():
    app = Flask(__name__,
        template_folder=str(TEMPLATES),
        static_folder=str(STATIC),
    )
    set_cookie_key()
    file = load_file()
    app.config["SECRET_KEY"] = file.cookie_key
    logger.info(f"Cookie Key: {app.config['SECRET_KEY']}")
    socketio.init_app(app, async_mode="threading", cors_allowed_origins="*")
    return app
