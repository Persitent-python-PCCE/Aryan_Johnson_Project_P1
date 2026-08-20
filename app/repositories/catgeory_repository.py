from app.extensions import db
from app.models.category import Category


class CategoryRepository:

    @staticmethod
    def create(name, description=None):
        category = Category(
            name=name,
            description=description
        )

        db.session.add(category)
        db.session.flush()

        return category

    @staticmethod
    def get_by_id(category_id):
        return db.session.get(Category, category_id)

    @staticmethod
    def get_by_name(name):
        return Category.query.filter_by(name=name).first()

    @staticmethod
    def get_all(active_only=False):
        query = Category.query

        if active_only:
            query = query.filter_by(is_active=True)

        return query.order_by(Category.name.asc()).all()

    @staticmethod
    def update(category, **kwargs):
        for field, value in kwargs.items():
            if hasattr(category, field):
                setattr(category, field, value)

        db.session.flush()

        return category

    @staticmethod
    def delete(category):
        db.session.delete(category)
        db.session.flush()