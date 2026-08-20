from flask import Blueprint, render_template, session

from app.utils.auth import role_required


customer_bp = Blueprint(
    "customer",
    __name__,
    url_prefix="/customer"
)


@customer_bp.route("/dashboard")
@role_required("CUSTOMER")
def dashboard():
    return render_template(
        "customer/dashboard.html",
        user_id=session.get("user_id")
    )