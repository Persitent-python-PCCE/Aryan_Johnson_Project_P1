from flask import Flask, jsonify, request
from dotenv import load_dotenv

from app.config import Config
from app.extensions import db, migrate, jwt
from app import models

from app.controllers.main_controller import main_bp
from app.controllers.auth_controller import auth_bp
from app.controllers.customer_controller import customer_bp
from app.controllers.admin_controller import admin_bp
from app.controllers.api import api_bp


def create_app(test_config=None):

    load_dotenv()

    app = Flask(__name__)

    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    register_api_error_handlers(app)

    return app


def register_api_error_handlers(app):

    @app.errorhandler(404)
    def handle_not_found(error):

        if request.path.startswith("/api/v1"):
            return jsonify({
                "status": "error",
                "message": "Resource not found"
            }), 404

        return error

    @app.errorhandler(405)
    def handle_method_not_allowed(error):

        if request.path.startswith("/api/v1"):
            return jsonify({
                "status": "error",
                "message": "Method not allowed"
            }), 405

        return error

    @app.errorhandler(500)
    def handle_internal_server_error(error):

        if request.path.startswith("/api/v1"):
            db.session.rollback()

            return jsonify({
                "status": "error",
                "message": "Internal server error"
            }), 500

        return error