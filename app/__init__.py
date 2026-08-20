from flask import Flask
from dotenv import load_dotenv

from app.config import Config
from app.extensions import db, migrate
from app.controllers.main_controller import main_bp
from app.models import Role, User


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main_bp)

    return app