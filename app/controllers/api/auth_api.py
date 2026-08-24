from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies
)

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

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "role": user.role.name,
                "email": user.email
            }
        )

        refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims={
                "role": user.role.name
            }
        )

        response = jsonify({
            "status": "success",
            "message": "Login successful",
            "data": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role.name
            }
        })

        set_access_cookies(
            response,
            access_token
        )

        set_refresh_cookies(
            response,
            refresh_token
        )

        return response, 200

    except ValueError as exc:

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 400


@api_bp.route(
    "/auth/refresh",
    methods=["POST"]
)
@jwt_required(
    refresh=True
)
def refresh():

    identity = get_jwt_identity()

    claims = get_jwt()

    access_token = create_access_token(
        identity=identity,
        additional_claims={
            "role": claims.get("role")
        }
    )

    response = jsonify({
        "status": "success",
        "message": "Access token refreshed"
    })

    set_access_cookies(
        response,
        access_token
    )

    return response, 200

@api_bp.route(
    "/auth/logout",
    methods=["POST"]
)
def logout():

    response = jsonify({
        "status": "success",
        "message": "Logout successful"
    })

    unset_jwt_cookies(
        response
    )

    return response, 200