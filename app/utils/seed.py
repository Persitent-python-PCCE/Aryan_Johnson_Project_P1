from app import create_app
from app.extensions import db
from app.models.role import Role


def seed_roles():
    app = create_app()

    with app.app_context():
        roles = [
            ("CUSTOMER", "Standard customer account"),
            ("ADMIN", "Administrator account"),
        ]

        for name, description in roles:
            existing_role = Role.query.filter_by(name=name).first()

            if existing_role is None:
                db.session.add(
                    Role(
                        name=name,
                        description=description
                    )
                )

        db.session.commit()
        print("Roles seeded successfully.")


if __name__ == "__main__":
    seed_roles()