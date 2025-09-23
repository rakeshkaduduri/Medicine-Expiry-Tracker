from src.config import get_supabase

class CategoryDAO:
    def __init__(self):
        self.sb = get_supabase()

    def create_category(self, name: str):
        self.sb.table("categories").insert({"name": name}).execute()
        resp = self.sb.table("categories").select("*").eq("name", name).limit(1).execute()
        return resp.data[0] if resp.data else None

    def list_categories(self):
        resp = self.sb.table("categories").select("*").execute()
        return resp.data or []

    def get_category_by_name(self, name: str):
        resp = self.sb.table("categories").select("*").eq("name", name).limit(1).execute()
        return resp.data[0] if resp.data else None
