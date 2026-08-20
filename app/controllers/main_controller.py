from flask import Blueprint

main_bp = Blueprint("main", __name__)


@main_bp.route("/health", methods=["GET"])
def health_check():
    return {
        "status": "success",
        "message": "Ticket Booking API is running"
    }, 200