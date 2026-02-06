from flask import Flask
from .extensions import socketio

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"

    socketio.init_app(app, async_mode="threading", cors_allowed_origins="*")
    return app
