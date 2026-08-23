from flask import jsonify, request, session

from app.controllers.api import api_bp
from app.services.auth_service import AuthService


@api_bp.route(
    "/auth/register",
    methods=["POST"]
)
def register():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request body must contain JSON"
        }), 400

    name = data.get("name", "")
    email = data.get("email", "")
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")

    if password != confirm_password:
        return jsonify({
            "status": "error",
            "message": "Passwords do not match"
        }), 400

    try:
        user = AuthService.register(
            name=name,
            email=email,
            password=password
        )

        return jsonify({
            "status": "success",
            "message": "Registration successful",
            "data": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role.name
            }
        }), 201

    except ValueError as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 400


@api_bp.route(
    "/auth/login",
    methods=["POST"]
)
def login():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request body must contain JSON"
        }), 400

    email = data.get(
        "email",
        ""
    )

    password = data.get(
        "password",
        ""
    )

    try:
        user = AuthService.authenticate(
            email=email,
            password=password
        )

        session.clear()

        session["user_id"] = user.id
        session["role"] = user.role.name

        return jsonify({
            "status": "success",
            "message": "Login successful",
            "data": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role.name
            }
        }), 200

    except ValueError as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 400


@api_bp.route(
    "/auth/logout",
    methods=["POST"]
)
def logout():

    session.clear()

    return jsonify({
        "status": "success",
        "message": "Logout successful"
    }), 200