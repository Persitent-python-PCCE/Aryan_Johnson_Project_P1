from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies
)

from app.extensions import db
from app.services.auth_service import AuthService
from app.services.file_service import FileService


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@auth_bp.route(
    "/register",
    methods=["GET", "POST"]
)
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

    document_type = request.form.get(
        "document_type",
        ""
    ).strip()

    uploaded_file = request.files.get(
        "document"
    )

    # --------------------------------------------------------
    # Password validation
    # --------------------------------------------------------

    if password != confirm_password:

        flash(
            "Passwords do not match.",
            "danger"
        )

        return render_template(
            "auth/register.html"
        )

    # --------------------------------------------------------
    # Optional document validation
    # --------------------------------------------------------

    if uploaded_file and uploaded_file.filename:

        if not document_type:

            flash(
                "Please select a document type.",
                "danger"
            )

            return render_template(
                "auth/register.html"
            )

    try:

        # ----------------------------------------------------
        # Create customer account
        # ----------------------------------------------------

        user = AuthService.register(
            name=name,
            email=email,
            password=password
        )

        # ----------------------------------------------------
        # Optional identity document
        # ----------------------------------------------------

        if uploaded_file and uploaded_file.filename:

            uploaded_file.stream.seek(0)

            file_size = uploaded_file.stream.seek(
                0,
                2
            )

            uploaded_file.stream.seek(0)

            try:

                FileService.save_document(
                    user_id=user.id,
                    document_type=document_type,
                    filename=uploaded_file.filename,
                    file_size=file_size,
                    mime_type=uploaded_file.mimetype,
                    file_object=uploaded_file
                )

                db.session.commit()

            except Exception:

                db.session.rollback()

                flash(
                    "Account created, but the identity document could not be uploaded. You can upload it later from My Documents.",
                    "warning"
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

    except Exception:

        db.session.rollback()

        flash(
            "Unable to complete registration.",
            "danger"
        )

        return render_template(
            "auth/register.html"
        )


@auth_bp.route(
    "/login",
    methods=["GET", "POST"]
)
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

        # ----------------------------------------------------
        # Flask session
        # ----------------------------------------------------

        session.clear()

        session["user_id"] = user.id
        session["role"] = user.role.name

        # ----------------------------------------------------
        # JWT access token
        # ----------------------------------------------------

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "role": user.role.name,
                "email": user.email
            }
        )

        # ----------------------------------------------------
        # JWT refresh token
        # ----------------------------------------------------

        refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims={
                "role": user.role.name
            }
        )

        # ----------------------------------------------------
        # Create redirect response
        # ----------------------------------------------------

        if user.role.name == "ADMIN":

            response = redirect(
                url_for(
                    "admin.dashboard"
                )
            )

        else:

            response = redirect(
                url_for(
                    "customer.dashboard"
                )
            )

        # ----------------------------------------------------
        # Store JWT tokens in cookies
        # ----------------------------------------------------

        set_access_cookies(
            response,
            access_token
        )

        set_refresh_cookies(
            response,
            refresh_token
        )

        flash(
            "Login successful.",
            "success"
        )

        return response

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

    response = redirect(
        url_for("auth.login")
    )

    unset_jwt_cookies(
        response
    )

    flash(
        "You have been logged out.",
        "success"
    )

    return response