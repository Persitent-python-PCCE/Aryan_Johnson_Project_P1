from app.extensions import db
from app.models.user import User


class UserRepository:

    @staticmethod
    def create(
        name,
        email,
        password_hash,
        role_id
    ):
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            role_id=role_id
        )

        db.session.add(user)
        db.session.flush()

        return user

    @staticmethod
    def get_by_id(user_id):
        return db.session.get(User, user_id)

    @staticmethod
    def get_by_email(email):
        return (
            User.query
            .filter(
                User.email == email
            )
            .first()
        )

    @staticmethod
    def get_by_role(role_id):
        return (
            User.query
            .filter(
                User.role_id == role_id
            )
            .all()
        )

    @staticmethod
    def get_all():
        return (
            User.query
            .order_by(
                User.id.asc()
            )
            .all()
        )

    @staticmethod
    def update(user, **kwargs):
        for field, value in kwargs.items():
            if hasattr(user, field):
                setattr(user, field, value)

        db.session.flush()

        return user

    @staticmethod
    def delete(user):
        db.session.delete(user)
        db.session.flush()