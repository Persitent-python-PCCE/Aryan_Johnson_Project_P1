from app.repositories.category_repository import CategoryRepository


class CategoryService:

    @staticmethod
    def create_category(name, description=None):
        existing_category = CategoryRepository.get_by_name(name)

        if existing_category:
            raise ValueError("Category already exists")

        return CategoryRepository.create(
            name=name,
            description=description
        )

    @staticmethod
    def get_category(category_id):
        category = CategoryRepository.get_by_id(category_id)

        if not category:
            raise ValueError("Category not found")

        return category

    @staticmethod
    def get_categories(active_only=False):
        return CategoryRepository.get_all(
            active_only=active_only
        )

    @staticmethod
    def update_category(category_id, **kwargs):
        category = CategoryService.get_category(category_id)

        if "name" in kwargs:
            existing_category = CategoryRepository.get_by_name(
                kwargs["name"]
            )

            if (
                existing_category
                and existing_category.id != category.id
            ):
                raise ValueError("Category already exists")

        return CategoryRepository.update(
            category,
            **kwargs
        )

    @staticmethod
    def delete_category(category_id):
        category = CategoryService.get_category(category_id)

        CategoryRepository.delete(category)

    @staticmethod
    def delete_category(category_id):
        category = CategoryRepository.get_by_id(category_id)

        if not category:
            raise ValueError("Category not found")

        if CategoryRepository.has_events(category_id):
            raise ValueError(
                "Cannot delete this category because events are using it."
            )

        CategoryRepository.delete(category)

        return category