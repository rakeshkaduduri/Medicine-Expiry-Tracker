from src.dao.category_dao import CategoryDAO

class CategoryService:
    def __init__(self, dao=None):
        self.dao = dao or CategoryDAO()

    def add_category(self, name: str):
        existing = self.dao.get_category_by_name(name)
        if existing:
            return existing
        return self.dao.create_category(name)

    def list_categories(self):
        return self.dao.list_categories()
