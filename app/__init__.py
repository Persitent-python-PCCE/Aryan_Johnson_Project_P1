from flask import Flask
from dotenv import load_dotenv

from app.config import Config
from app.extensions import db, migrate

from app.controllers.main_controller import main_bp
from app.controllers.auth_controller import auth_bp
from app.controllers.customer_controller import customer_bp
from app.controllers.admin_controller import admin_bp


def create_app(test_config=None):
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(admin_bp)

    return app