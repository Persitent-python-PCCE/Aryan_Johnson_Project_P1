from flask import jsonify

from app.controllers.api import api_bp


@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "success",
            "message": "Ticket Booking API is running"
        }
    )