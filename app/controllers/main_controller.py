from flask import Blueprint, jsonify, render_template


main_bp = Blueprint(
    "main",
    __name__
)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/health")
def health_check():
    return jsonify(
        {
            "status": "success",
            "message": "Ticket Booking API is running"
        }
    )


@main_bp.route("/unauthorized")
def unauthorized():
    return render_template(
        "errors/unauthorized.html"
    ), 403