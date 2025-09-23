from typing import List, Dict
from src.config import get_supabase

class AlertDAO:
    def __init__(self):
        self.sb = get_supabase()

    def add_alert(self, medicine_id: int, alert_date: str, status: str = "Pending") -> Dict:
        payload = {"medicine_id": medicine_id, "alert_date": alert_date, "status": status}
        self.sb.table("alerts").insert(payload).execute()
        resp = self.sb.table("alerts").select("*").eq("medicine_id", medicine_id).eq("alert_date", alert_date).limit(1).execute()
        return resp.data[0] if resp.data else None

    def list_pending_alerts(self) -> List[Dict]:
        resp = self.sb.table("alerts").select("*").eq("status", "Pending").execute()
        return resp.data or []

    def update_alert_status(self, alert_id: int, status: str):
        self.sb.table("alerts").update({"status": status}).eq("id", alert_id).execute()
