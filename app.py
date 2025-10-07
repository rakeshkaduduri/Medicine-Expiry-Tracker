# app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.services.category_service import CategoryService
from src.services.medicine_service import MedicineService

# -------------------------------------
# Streamlit page setup
# -------------------------------------
st.set_page_config(page_title="💊 Medicine Expiry Tracker", layout="wide")

# -------------------------------------
# Custom CSS for cards, tables, centered data, and sidebar
# -------------------------------------
st.markdown("""
    <style>
        /* Main background */
        .main {
            background: linear-gradient(135deg, #f7f9fc 0%, #eef3f8 100%);
        }

        /* Metric cards */
        .metric-card {
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            color: white;
        }
        .metric-title {
            font-size: 18px;
            font-weight: 500;
        }
        .metric-value {
            font-size: 26px;
            font-weight: 700;
        }

        /* Tables */
        th {
            background-color: #1976d2 !important;
            color: white !important;
            text-align: center !important;
        }
        td {
            text-align: center !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: rgba(25, 118, 210, 1); 
            color: white;
            font-family: 'Poppins', sans-serif;
            padding: 15px 10px;
        }
        div[data-testid="stRadio"] > div {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        div[data-testid="stRadio"] label {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
            padding: 10px 12px;
            border-radius: 10px;
            transition: all 0.3s ease;
            color: #f5f5f5 !important;
        }
        div[data-testid="stRadio"] label:hover {
            background-color: rgba(255, 255, 255, 0.15);
        }
        div[data-testid="stRadio"] input:checked + div > label {
            background-color: #ffca28 !important;
            color: #1a237e !important;
            font-weight: 700;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------
# Initialize services
# -------------------------------------
cat_service = CategoryService()
med_service = MedicineService()

# -------------------------------------
# Helper functions
# -------------------------------------
def fetch_categories():
    return cat_service.list_categories() or []

def fetch_medicines():
    return med_service.list_medicines() or []

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        return None

def categorize_medicine(expiry_date):
    today = datetime.today().date()
    if expiry_date < today:
        return "Expired", "#ff4b4b"  # Red
    elif expiry_date <= today + timedelta(days=7):
        return "Expiring Soon", "#ffb84b"  # Orange
    else:
        return "Safe", "#4caf50"  # Green

def format_date_range(created_at, expiry_date):
    try:
        c_date = created_at.split("T")[0]
        e_date = expiry_date
        return f"{c_date} - {e_date}"
    except:
        return f"{created_at} - {expiry_date}"

# -------------------------------------
# Sidebar Navigation
# -------------------------------------
st.sidebar.markdown("""
    <div style="text-align:center; margin-bottom:15px;">
        <h2 style="color:#ffca28; font-weight:700; margin-bottom:5px;">💊 Medicine Tracker</h2>
        <div style="font-size:18px; color:#ffffff; font-weight:600; border-bottom:2px solid #ffca28; padding-bottom:5px;">
            Navigate
        </div>
    </div>
""", unsafe_allow_html=True)

section = st.sidebar.radio(
    "",
    ["📊 Dashboard", "📋 View Medicines", "➕ Add Medicine", "⏰ Expiring Soon", "🔔 Alerts", "🗑 Delete Expired"]
)
st.sidebar.markdown("---")
st.sidebar.caption("💊 Medicine Expiry Tracker | Supabase Backend")

# -------------------------------------
# Section: Dashboard
# -------------------------------------
if section == "📊 Dashboard":
    st.title("📊 Dashboard Overview")

    medicines = fetch_medicines()
    categories = fetch_categories()

    expired = [m for m in medicines if parse_date(m["expiry_date"]) and parse_date(m["expiry_date"]) < datetime.today().date()]
    expiring = [m for m in medicines if parse_date(m["expiry_date"]) and datetime.today().date() <= parse_date(m["expiry_date"]) <= datetime.today().date() + timedelta(days=7)]
    
    total_meds = len(medicines)
    total_cats = len(categories)
    expired_count = len(expired)
    expiring_count = len(expiring)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="metric-card" style="background-color:#2e7d32;">
                <div class="metric-title">Total Medicines</div>
                <div class="metric-value">{total_meds}</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card" style="background-color:#1976d2;">
                <div class="metric-title">Categories</div>
                <div class="metric-value">{total_cats}</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card" style="background-color:#ff9800;">
                <div class="metric-title">Expiring Soon</div>
                <div class="metric-value">{expiring_count}</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="metric-card" style="background-color:#d32f2f;">
                <div class="metric-title">Expired</div>
                <div class="metric-value">{expired_count}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📅 Medicines Summary Table")
    if total_meds == 0:
        st.info("No medicines found. Add some from the sidebar!")
    else:
        df = pd.DataFrame(medicines)
        df["status"] = df["expiry_date"].apply(lambda d: categorize_medicine(parse_date(d))[0])
        df["date_range"] = df.apply(lambda x: format_date_range(x["created_at"], x["expiry_date"]), axis=1)
        st.dataframe(df[["id","name","quantity","date_range","status"]], use_container_width=True)

# -------------------------------------
# Section: View Medicines
# -------------------------------------
elif section == "📋 View Medicines":
    st.title("📋 All Medicines by Category")
    categories = fetch_categories()
    meds = fetch_medicines()
    if not meds:
        st.info("No medicines available.")
    else:
        df = pd.DataFrame(meds)
        df["status"], df["color"] = zip(*df["expiry_date"].apply(lambda d: categorize_medicine(parse_date(d))))
        df["date_range"] = df.apply(lambda x: format_date_range(x["created_at"], x["expiry_date"]), axis=1)
        for cat in categories:
            cat_meds = df[df["category_id"] == cat["id"]]
            if not cat_meds.empty:
                st.markdown(f"### 🧾 {cat['name']}")
                st.dataframe(cat_meds[["id","name","quantity","date_range","status"]], use_container_width=True)

# -------------------------------------
# Section: Add Medicine
# -------------------------------------
elif section == "➕ Add Medicine":
    st.title("➕ Add a New Medicine")
    categories = fetch_categories()
    cat_names = [c["name"] for c in categories] if categories else []

    name = st.text_input("Medicine Name")
    expiry = st.date_input("Expiry Date")
    quantity = st.number_input("Quantity", min_value=1, value=1)
    new_cat = st.text_input("Or enter new category")
    selected_cat = st.selectbox("Select existing category", ["-- choose --"] + cat_names)

    if st.button("Add / Update Medicine"):
        cat_name = new_cat or (selected_cat if selected_cat != "-- choose --" else None)
        if not name or not cat_name:
            st.error("Please enter medicine name and category.")
        else:
            category = cat_service.add_category(cat_name)
            med = med_service.add_medicine(name, expiry.strftime("%Y-%m-%d"), category["id"], quantity)
            st.success(f"✅ '{name}' added successfully under '{cat_name}'!")

# -------------------------------------
# Section: Expiring Soon
# -------------------------------------
elif section == "⏰ Expiring Soon":
    st.title("⏰ Medicines Expiring Soon")
    days = st.slider("Show medicines expiring within days", 1, 90, 7)
    meds = fetch_medicines()
    soon = [m for m in meds if parse_date(m["expiry_date"]) and datetime.today().date() <= parse_date(m["expiry_date"]) <= datetime.today().date() + timedelta(days=days)]

    if not soon:
        st.success(f"No medicines expiring in next {days} days 🎉")
    else:
        df = pd.DataFrame(soon)
        df["status"] = "Expiring Soon"
        df["date_range"] = df.apply(lambda x: format_date_range(x["created_at"], x["expiry_date"]), axis=1)
        st.dataframe(df[["id","name","quantity","date_range","status"]], use_container_width=True)

# -------------------------------------
# Section: Alerts
# -------------------------------------
elif section == "🔔 Alerts":
    st.title("🔔 Pending Alerts")
    alerts = []
    if hasattr(med_service, "alert_dao") and hasattr(med_service.alert_dao, "list_pending_alerts"):
        alerts = med_service.alert_dao.list_pending_alerts()
    if not alerts:
        st.info("No pending alerts found.")
    else:
        df = pd.DataFrame(alerts)
        st.dataframe(df, use_container_width=True)

# -------------------------------------
# Section: Delete Expired
# -------------------------------------
elif section == "🗑 Delete Expired":
    st.title("🗑 Delete Expired Medicines")
    meds = fetch_medicines()
    expired = [m for m in meds if parse_date(m["expiry_date"]) and parse_date(m["expiry_date"]) < datetime.today().date()]

    if not expired:
        st.success("No expired medicines found ✅")
    else:
        st.warning(f"Found {len(expired)} expired medicines.")

        # Create DataFrame
        df = pd.DataFrame(expired)

        # Add status column
        df["status"] = df["expiry_date"].apply(lambda d: categorize_medicine(parse_date(d))[0])

        # Add formatted date range column
        df["date_range"] = df.apply(lambda x: format_date_range(x["created_at"], x["expiry_date"]), axis=1)

        # Display the DataFrame
        st.dataframe(df[["id", "name", "quantity", "date_range", "status"]], use_container_width=True)

        # Delete button
        if st.button("Delete All Expired"):
            for m in expired:
                if hasattr(med_service, "med_dao") and hasattr(med_service.med_dao, "update_medicine"):
                    med_service.med_dao.update_medicine(m["id"], {"quantity": 0})
            st.success("✅ Expired medicines deleted successfully!")