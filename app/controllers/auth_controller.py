from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from app.services.auth_service import AuthService


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template(
            "auth/register.html"
        )

    name = request.form.get(
        "name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )

    confirm_password = request.form.get(
        "confirm_password",
        ""
    )

    if password != confirm_password:
        flash(
            "Passwords do not match.",
            "danger"
        )

        return render_template(
            "auth/register.html"
        )

    try:
        AuthService.register(
            name=name,
            email=email,
            password=password
        )

        flash(
            "Registration successful. Please log in.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    except ValueError as exc:
        flash(
            str(exc),
            "danger"
        )

        return render_template(
            "auth/register.html"
        )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template(
            "auth/login.html"
        )

    email = request.form.get(
        "email",
        ""
    ).strip()

    password = request.form.get(
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

        flash(
            "Login successful.",
            "success"
        )

        # Temporary destination until the
        # actual customer/admin dashboards
        # are implemented.
        return redirect(
            url_for("main.health_check")
        )

    except ValueError as exc:
        flash(
            str(exc),
            "danger"
        )

        return render_template(
            "auth/login.html"
        )


@auth_bp.route("/logout")
def logout():
    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )