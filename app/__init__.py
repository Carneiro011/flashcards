# app/__init__.py

from flask import Flask
from config import config

def create_app(config_name: str = "default") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Registra o blueprint (grupo de rotas) do controller
    from app.controllers.flashcard_controller import flashcard_bp
    app.register_blueprint(flashcard_bp)

    return app