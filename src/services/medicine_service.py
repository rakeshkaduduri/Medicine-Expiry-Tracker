from typing import List, Dict
from datetime import datetime, timedelta
from src.dao.medicine_dao import MedicineDAO
from src.dao.alert_dao import AlertDAO

class MedicineService:
    def __init__(self, med_dao=None, alert_dao=None):
        self.med_dao = med_dao or MedicineDAO()
        self.alert_dao = alert_dao or AlertDAO()

    def add_medicine(self, name: str, expiry_date: str, category_id: int, quantity: int = 1) -> Dict:
        med = self.med_dao.add_medicine(name, expiry_date, category_id, quantity)
        # Add alert 7 days before expiry
        expiry_dt = datetime.strptime(expiry_date, "%Y-%m-%d")
        alert_dt = expiry_dt - timedelta(days=7)
        self.alert_dao.add_alert(med["id"], alert_dt.strftime("%Y-%m-%d"))
        return med

    def list_medicines(self) -> List[Dict]:
        return self.med_dao.list_medicines()

    def get_expiring_soon(self) -> List[Dict]:
        pending_alerts = self.alert_dao.list_pending_alerts()
        today_str = datetime.today().strftime("%Y-%m-%d")
        return [alert for alert in pending_alerts if alert["alert_date"] <= today_str]

    def mark_alert_sent(self, alert_id: int):
        self.alert_dao.update_alert_status(alert_id, "Sent")
