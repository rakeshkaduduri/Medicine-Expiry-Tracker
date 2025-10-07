'''Medicine-Expiry-Tracker/
│
├─ src/
│  ├─ __init__.py
│  ├─ cli/
│  │  ├─ __init__.py
│  │  └─ main.py
│  ├─ services/
│  │  ├─ __init__.py
│  │  ├─ medicine_service.py
│  │  └─ category_service.py
│  └─ dao/
│     ├─ __init__.py
│     ├─ medicine_dao.py
│     └─ category_dao.py
│     └─ alert_dao.py
│  └─ config.py
└─ .env
'''


# src/cli/main.py
import argparse
import json
from datetime import datetime
from src.services import category_service, medicine_service

class CLIApp:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog="medicine-cli")
        self.subparsers = self.parser.add_subparsers(dest="cmd")

        self.cat_service = category_service.CategoryService()
        self.med_service = medicine_service.MedicineService()

        self._build_commands()

    def _build_commands(self):
        # ------------------------
        # Category commands
        # ------------------------
        cat_parser = self.subparsers.add_parser("category", help="category commands")
        cat_sub = cat_parser.add_subparsers(dest="action")

        addc = cat_sub.add_parser("add")
        addc.add_argument("--name", required=True)
        addc.set_defaults(func=self.add_category)

        listc = cat_sub.add_parser("list")
        listc.set_defaults(func=self.list_categories)

        # ------------------------
        # Medicine commands
        # ------------------------
        med_parser = self.subparsers.add_parser("medicine", help="medicine commands")
        med_sub = med_parser.add_subparsers(dest="action")

        addm = med_sub.add_parser("add")
        addm.add_argument("--name", required=True)
        addm.add_argument("--expiry_date", required=True, help="YYYY-MM-DD")
        addm.add_argument("--category_name", required=True, help="Category name for the medicine")
        addm.add_argument("--quantity", type=int, default=1)
        addm.set_defaults(func=self.add_medicine)

        listm = med_sub.add_parser("list")
        listm.set_defaults(func=self.list_medicines)

        expiring = med_sub.add_parser("expiring")
        expiring.set_defaults(func=self.list_expiring)

        delete_expired = med_sub.add_parser("delete_expired")
        delete_expired.set_defaults(func=self.delete_expired_medicines)

        # ------------------------
        # Alert commands
        # ------------------------
        alert_parser = self.subparsers.add_parser("alert", help="alert commands")
        alert_sub = alert_parser.add_subparsers(dest="action")

        list_pending = alert_sub.add_parser("list_pending")
        list_pending.set_defaults(func=self.list_pending_alerts)

    # ------------------------
    # Handlers
    # ------------------------
    def add_category(self, args):
        c = self.cat_service.add_category(args.name)
        print("Category Added:", json.dumps(c, indent=2))

    def list_categories(self, args):
        cats = self.cat_service.list_categories()
        print(json.dumps(cats, indent=2))

    def add_medicine(self, args):
        # Fetch or create category by name
        category = self.cat_service.add_category(args.category_name)
        category_id = category["id"]

        m = self.med_service.add_medicine(args.name, args.expiry_date, category_id, args.quantity)
        print("Medicine Added:", json.dumps(m, indent=2))

    def list_medicines(self, args):
        meds = self.med_service.list_medicines()
        print(json.dumps(meds, indent=2))

    def list_expiring(self, args):
        alerts = self.med_service.get_expiring_soon()
        if not alerts:
            print("No medicines expiring soon!")
        else:
            print("Expiring Soon Alerts:")
            print(json.dumps(alerts, indent=2))

    def list_pending_alerts(self, args):
        alerts = self.med_service.get_expiring_soon()
        if not alerts:
            print("No pending alerts!")
        else:
            print("Pending Alerts:")
            print(json.dumps(alerts, indent=2))

    def delete_expired_medicines(self, args):
        today_str = datetime.today().strftime("%Y-%m-%d")
        all_meds = self.med_service.list_medicines()
        deleted = []
        for med in all_meds:
            if med["expiry_date"] <= today_str:
                self.med_service.med_dao.update_medicine(med["id"], {"quantity": 0})  # or delete if needed
                deleted.append(med)
        if not deleted:
            print("No expired medicines to delete.")
        else:
            print("Deleted Expired Medicines:")
            print(json.dumps(deleted, indent=2))

    # ------------------------
    # Run
    # ------------------------
    def run(self):
        args = self.parser.parse_args()
        if not hasattr(args, "func"):
            self.parser.print_help()
            return
        args.func(args)

if __name__ == "__main__":
    CLIApp().run()
