from app.repositories.role_repository import RoleRepository


class RoleService:

    ALLOWED_ROLES = {
        "CUSTOMER",
        "ADMIN"
    }

    @staticmethod
    def create_role(name, description=None):
        name = name.upper()

        if name not in RoleService.ALLOWED_ROLES:
            raise ValueError("Invalid role")

        existing_role = RoleRepository.get_by_name(name)

        if existing_role:
            raise ValueError("Role already exists")

        return RoleRepository.create(
            name=name,
            description=description
        )

    @staticmethod
    def get_role(role_id):
        role = RoleRepository.get_by_id(role_id)

        if not role:
            raise ValueError("Role not found")

        return role

    @staticmethod
    def get_role_by_name(name):
        role = RoleRepository.get_by_name(
            name.upper()
        )

        if not role:
            raise ValueError("Role not found")

        return role

    @staticmethod
    def get_roles():
        return RoleRepository.get_all()