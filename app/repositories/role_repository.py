from app.extensions import db
from app.models.role import Role


class RoleRepository:

    @staticmethod
    def create(name, description=None):
        role = Role(
            name=name,
            description=description
        )

        db.session.add(role)
        db.session.flush()

        return role

    @staticmethod
    def get_by_id(role_id):
        return db.session.get(Role, role_id)

    @staticmethod
    def get_by_name(name):
        return (
            Role.query
            .filter(
                Role.name == name
            )
            .first()
        )

    @staticmethod
    def get_all():
        return (
            Role.query
            .order_by(
                Role.id.asc()
            )
            .all()
        )

    @staticmethod
    def update(role, **kwargs):
        for field, value in kwargs.items():
            if hasattr(role, field):
                setattr(role, field, value)

        db.session.flush()

        return role

    @staticmethod
    def delete(role):
        db.session.delete(role)
        db.session.flush()