from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository


class UserService:

    @staticmethod
    def get_user(user_id):
        user = UserRepository.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        return user

    @staticmethod
    def get_user_by_email(email):
        user = UserRepository.get_by_email(email)

        if not user:
            raise ValueError("User not found")

        return user

    @staticmethod
    def get_users_by_role(role_id):
        role = RoleRepository.get_by_id(role_id)

        if not role:
            raise ValueError("Role not found")

        return UserRepository.get_by_role(role_id)

    @staticmethod
    def update_user(user_id, **kwargs):
        user = UserService.get_user(user_id)

        if "email" in kwargs:
            existing_user = UserRepository.get_by_email(
                kwargs["email"]
            )

            if (
                existing_user
                and existing_user.id != user.id
            ):
                raise ValueError("Email already exists")

        if "role_id" in kwargs:
            role = RoleRepository.get_by_id(
                kwargs["role_id"]
            )

            if not role:
                raise ValueError("Role not found")

        return UserRepository.update(
            user,
            **kwargs
        )

    @staticmethod
    def deactivate_user(user_id):
        user = UserService.get_user(user_id)

        return UserRepository.update(
            user,
            is_active=False
        )

    @staticmethod
    def activate_user(user_id):
        user = UserService.get_user(user_id)

        return UserRepository.update(
            user,
            is_active=True
        )