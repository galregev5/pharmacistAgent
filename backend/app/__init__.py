"""Flask application factory."""

from flask import Flask
from flask_cors import CORS

from config import Config


def create_app() -> Flask:
	app = Flask(__name__)
	app.config.from_object(Config)

	CORS(app)

	from app.routes import main

	app.register_blueprint(main)

	return app
