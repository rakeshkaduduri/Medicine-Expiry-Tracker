from typing import Optional, List, Dict
from src.config import get_supabase

class MedicineDAO:
    def __init__(self):
        self.sb = get_supabase()

    def add_medicine(self, name: str, expiry_date: str, category_id: int, quantity: int = 1) -> Dict:
        # Check if medicine already exists under same category
        resp = self.sb.table("medicines")\
            .select("*")\
            .eq("name", name)\
            .eq("category_id", category_id)\
            .limit(1)\
            .execute()
        existing = resp.data[0] if resp.data else None

        if existing:
            # Update quantity
            new_qty = existing["quantity"] + quantity
            self.sb.table("medicines").update({"quantity": new_qty}).eq("id", existing["id"]).execute()
            return self.get_medicine_by_id(existing["id"])

        # Otherwise insert new medicine
        payload = {"name": name, "expiry_date": expiry_date, "category_id": category_id, "quantity": quantity}
        self.sb.table("medicines").insert(payload).execute()
        resp = self.sb.table("medicines")\
            .select("*")\
            .eq("name", name)\
            .eq("category_id", category_id)\
            .limit(1)\
            .execute()
        return resp.data[0] if resp.data else None

    def list_medicines(self) -> List[Dict]:
        resp = self.sb.table("medicines").select("*").execute()
        return resp.data or []

    def get_medicine_by_id(self, med_id: int) -> Optional[Dict]:
        resp = self.sb.table("medicines").select("*").eq("id", med_id).limit(1).execute()
        return resp.data[0] if resp.data else None
