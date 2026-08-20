from app.extensions import db

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository


class AuthService:

    MIN_PASSWORD_LENGTH = 8

    @staticmethod
    def register(
        name,
        email,
        password,
        role_name="CUSTOMER"
    ):
        if not name or not name.strip():
            raise ValueError("Name is required")

        if not email or not email.strip():
            raise ValueError("Email is required")

        if not password:
            raise ValueError("Password is required")

        if len(password) < AuthService.MIN_PASSWORD_LENGTH:
            raise ValueError(
                "Password must be at least 8 characters"
            )

        email = email.strip().lower()
        role_name = role_name.strip().upper()

        existing_user = UserRepository.get_by_email(
            email
        )

        if existing_user:
            raise ValueError(
                "Email already exists"
            )

        role = RoleRepository.get_by_name(
            role_name
        )

        if not role:
            raise ValueError("Role not found")

        password_hash = generate_password_hash(
            password
        )

        try:
            user = UserRepository.create(
                name=name.strip(),
                email=email,
                password_hash=password_hash,
                role_id=role.id
            )

            db.session.commit()

            return user
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def authenticate(email, password):
        if not email or not password:
            raise ValueError(
                "Email and password are required"
            )

        email = email.strip().lower()

        user = UserRepository.get_by_email(
            email
        )

        if not user:
            raise ValueError(
                "Invalid email or password"
            )

        if hasattr(user, "is_active") and not user.is_active:
            raise ValueError(
                "Account is inactive"
            )

        if not check_password_hash(
            user.password_hash,
            password
        ):
            raise ValueError(
                "Invalid email or password"
            )

        return user