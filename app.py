"""
Khwezi Mining Health, Safety & Equipment Monitoring Application
MINN2020A – Computer Programming for Mining
University of the Witwatersrand – School of Mining Engineering

Run with:  streamlit run app.py
"""

import os
import json
import base64
import hashlib
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# =====================================================================
# CONFIGURATION
# =====================================================================
st.set_page_config(
    page_title="Khwezi Mining Monitor",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = "data"

# Educational prototype thresholds (NOT real mine safety limits)
TEMP_WARNING = 80.0
TEMP_CRITICAL = 100.0
VIB_WARNING = 5.0
VIB_CRITICAL = 8.0
FATIGUE_HIGH = 7
DOWNTIME_HIGH = 300
AVAILABILITY_LOW = 80.0

# =====================================================================
# RBAC
# =====================================================================
PAGES = {
    "dashboard":   "📊 Dashboard",
    "workers":     "👷 Worker Safety",
    "incidents":   "🚨 Safety Incidents",
    "equipment":   "🚜 Equipment",
    "condition":   "🌡️ Condition Monitoring",
    "maintenance": "🔧 Maintenance",
    "risk":        "⚠️ Risk Assessment",
    "alerts":      "🔔 Alerts",
    "analytics":   "📈 Analytics",
    "reports":     "📄 Reports",
    "users":       "👥 Manage Users",
}

PERMISSIONS = {
    "Administrator":        list(PAGES.keys()),
    "Safety Officer":       ["dashboard", "workers", "incidents", "risk", "alerts", "analytics", "reports"],
    "Mining Engineer":      ["dashboard", "workers", "incidents", "equipment", "condition", "maintenance", "risk", "alerts", "analytics", "reports"],
    "Maintenance Engineer": ["dashboard", "equipment", "condition", "maintenance", "alerts", "analytics", "reports"],
    "Manager":              ["dashboard", "workers", "incidents", "equipment", "maintenance", "risk", "alerts", "analytics", "reports"],
}

# =====================================================================
# HELPERS
# =====================================================================
def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def get_bg_image_url() -> str:
    """Look for a local Khwezi background image; return a base64 data URI."""
    candidates = ["khwezi_bg.jpg", "khwezi_bg.jpeg", "khwezi_bg.png", "assets/khwezi_bg.jpg"]
    for name in candidates:
        if os.path.exists(name):
            ext = name.rsplit(".", 1)[-1].lower()
            mime = "jpeg" if ext in ("jpg", "jpeg") else "png"
            try:
                with open(name, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                return f"data:image/{mime};base64,{b64}"
            except Exception:
                return ""
    return ""


# =====================================================================
# DATA GENERATION (runs once on first launch)
# =====================================================================
def generate_data(force: bool = False):
    ensure_data_dir()
    random.seed(42)
    np.random.seed(42)

    # ---------------- USERS ----------------
    users_path = os.path.join(DATA_DIR, "users.json")
    if force or not os.path.exists(users_path):
        users = {
            "admin":   {"password": hash_pw("admin123"),   "role": "Administrator",        "name": "Reatile Motang"},
            "safety":  {"password": hash_pw("safety123"),  "role": "Safety Officer",       "name": "Simphiwe Nkwanyana"},
            "mining":  {"password": hash_pw("mining123"),  "role": "Mining Engineer",      "name": "Tumelo Moatlhodi"},
            "maint":   {"password": hash_pw("maint123"),   "role": "Maintenance Engineer", "name": "Humbulani Maselesele"},
            "manager": {"password": hash_pw("manager123"), "role": "Manager",              "name": "Milka Madahana"},
        }
        with open(users_path, "w") as f:
            json.dump(users, f, indent=2)

    # ---------------- WORKERS ----------------
    workers_path = os.path.join(DATA_DIR, "workers.csv")
    if force or not os.path.exists(workers_path):
        departments = ["Underground", "Open Pit", "Processing", "Maintenance", "Engineering"]
        roles = ["Operator", "Driller", "Blaster", "Fitter", "Electrician", "Supervisor"]
        shifts = ["Day", "Night"]
        rows = []
        for i in range(1, 61):
            dept = random.choice(departments)
            role = random.choice(roles)
            shift = random.choice(shifts)
            ppe = random.choices(["Compliant", "Non-Compliant"], weights=[0.85, 0.15])[0]
            training = random.choices(["Valid", "Expired"], weights=[0.9, 0.1])[0]
            fatigue = int(np.clip(np.random.normal(4.5, 2), 1, 10))
            obs = random.randint(0, 5)
            near = random.randint(0, 3)
            prev = random.randint(0, 2)
            if fatigue >= FATIGUE_HIGH or ppe == "Non-Compliant" or training == "Expired":
                risk = random.choice(["High", "Critical"])
            elif fatigue >= 5 or near >= 2:
                risk = "Medium"
            else:
                risk = "Low"
            rows.append({
                "Worker ID": f"WRK-{i:03d}",
                "Department": dept,
                "Job Role": role,
                "Shift": shift,
                "PPE Compliance": ppe,
                "Safety Training": training,
                "Fatigue Level": fatigue,
                "Safety Observations": obs,
                "Near Misses": near,
                "Previous Incidents": prev,
                "Risk Level": risk,
            })
        pd.DataFrame(rows).to_csv(workers_path, index=False)

    # ---------------- INCIDENTS ----------------
    incidents_path = os.path.join(DATA_DIR, "incidents.csv")
    if force or not os.path.exists(incidents_path):
        departments = ["Underground", "Open Pit", "Processing", "Maintenance", "Engineering"]
        locations = ["Shaft A", "Shaft B", "Pit 1", "Pit 2", "Plant", "Workshop", "Stockpile"]
        types = ["Slip/Fall", "Equipment Failure", "Struck by Object", "Caught In/Between",
                 "Chemical Exposure", "Electrical", "Fire", "Other"]
        severities = ["Minor", "Moderate", "Major", "Critical"]
        statuses = ["Open", "In Progress", "Closed"]
        causes = ["Human error", "Equipment failure", "Poor visibility", "Wet floor",
                  "Lack of PPE", "Fatigue", "Inadequate training"]
        rows = []
        start = datetime.now() - timedelta(days=180)
        for i in range(1, 121):
            dt = start + timedelta(days=random.randint(0, 180),
                                   hours=random.randint(0, 23),
                                   minutes=random.randint(0, 59))
            sev = random.choices(severities, weights=[0.5, 0.3, 0.15, 0.05])[0]
            injured = "Yes" if random.random() < 0.35 else "No"
            lti = "Yes" if injured == "Yes" and random.random() < 0.4 else "No"
            rows.append({
                "Incident ID": f"INC-{i:04d}",
                "Date": dt.strftime("%Y-%m-%d"),
                "Time": dt.strftime("%H:%M"),
                "Shift": "Day" if 6 <= dt.hour < 18 else "Night",
                "Location": random.choice(locations),
                "Department": random.choice(departments),
                "Incident Type": random.choice(types),
                "Severity": sev,
                "Injury": injured,
                "Lost-Time Injury": lti,
                "Cause": random.choice(causes),
                "Corrective Action": "Pending" if random.random() < 0.3 else "Implemented",
                "Status": random.choice(statuses),
            })
        pd.DataFrame(rows).to_csv(incidents_path, index=False)

    # ---------------- EQUIPMENT ----------------
    equipment_path = os.path.join(DATA_DIR, "equipment.csv")
    if force or not os.path.exists(equipment_path):
        types_map = {
            "Haul Truck": "TRK", "Loader": "LDR", "Excavator": "EXC",
            "Drill": "DRL", "Bulldozer": "BLD", "Scraper Winch": "SCR",
            "Crusher": "CRS", "Conveyor": "CNV",
        }
        manufacturers = ["Caterpillar", "Komatsu", "Hitachi", "Sandvik", "Atlas Copco", "Joy Global"]
        rows = []
        counter = 1
        for etype, prefix in types_map.items():
            for _ in range(4):
                op = random.randint(1000, 8000)
                dt = random.randint(50, 600)
                temp = float(np.clip(np.random.normal(75, 20), 40, 130))
                vib = float(np.clip(np.random.normal(5, 3), 0.5, 14))
                rows.append({
                    "Equipment ID": f"{prefix}-{counter:03d}",
                    "Equipment Type": etype,
                    "Manufacturer": random.choice(manufacturers),
                    "Operating Hours": op,
                    "Downtime": dt,
                    "Temperature (C)": round(temp, 1),
                    "Vibration (mm/s)": round(vib, 2),
                    "Fuel Consumption (L/h)": round(random.uniform(8, 45), 1),
                    "Brake Status": random.choice(["OK", "Worn", "Faulty"]),
                    "Tyre Status": random.choice(["OK", "Worn", "Faulty"]),
                    "Engine Status": random.choice(["OK", "Warning", "Faulty"]),
                    "Maintenance Status": random.choice(["Up to date", "Due", "Overdue", "Under Maintenance"]),
                })
                counter += 1
        df = pd.DataFrame(rows)
        df["Availability (%)"] = (df["Operating Hours"] /
                                  (df["Operating Hours"] + df["Downtime"]) * 100).round(1)
        df.to_csv(equipment_path, index=False)

    # ---------------- MAINTENANCE ----------------
    maint_path = os.path.join(DATA_DIR, "maintenance.csv")
    if force or not os.path.exists(maint_path):
        rows = []
        for i in range(1, 41):
            rows.append({
                "Maintenance ID": f"MNT-{i:03d}",
                "Equipment ID": f"TRK-{random.randint(1,32):03d}",
                "Date": (datetime.now() - timedelta(days=random.randint(1, 180))).strftime("%Y-%m-%d"),
                "Type": random.choice(["Preventive", "Corrective", "Inspection"]),
                "Status": random.choice(["Completed", "In Progress", "Scheduled", "Overdue"]),
                "Cost (R)": random.randint(5000, 250000),
                "Notes": random.choice(["Routine service", "Bearing replaced", "Hydraulic leak fixed",
                                        "Engine overhaul", "Brake inspection"]),
            })
        pd.DataFrame(rows).to_csv(maint_path, index=False)


# =====================================================================
# DATA LOADERS
# =====================================================================
@st.cache_data
def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, name))


def load_users() -> dict:
    with open(os.path.join(DATA_DIR, "users.json")) as f:
        return json.load(f)


def save_users(users: dict):
    with open(os.path.join(DATA_DIR, "users.json"), "w") as f:
        json.dump(users, f, indent=2)


# =====================================================================
# BUSINESS LOGIC
# =====================================================================
def temp_status(t: float) -> str:
    if t > TEMP_CRITICAL:
        return "CRITICAL"
    if t >= TEMP_WARNING:
        return "WARNING"
    return "NORMAL"


def vib_status(v: float) -> str:
    if v > VIB_CRITICAL:
        return "CRITICAL"
    if v >= VIB_WARNING:
        return "WARNING"
    return "NORMAL"


def overall_status(row) -> str:
    s = [temp_status(row["Temperature (C)"]), vib_status(row["Vibration (mm/s)"])]
    if "CRITICAL" in s:
        return "CRITICAL"
    if "WARNING" in s:
        return "WARNING"
    return "NORMAL"


def risk_classification(score: int) -> str:
    if score >= 17:
        return "Critical"
    if score >= 10:
        return "High"
    if score >= 5:
        return "Medium"
    return "Low"


def build_alerts(workers: pd.DataFrame, incidents: pd.DataFrame, equipment: pd.DataFrame) -> pd.DataFrame:
    alerts = []

    for _, row in equipment.iterrows():
        ts = temp_status(row["Temperature (C)"])
        vs = vib_status(row["Vibration (mm/s)"])
        if ts == "CRITICAL":
            alerts.append({"Level": "CRITICAL", "Category": "Equipment",
                           "Source": row["Equipment ID"],
                           "Message": f"Temperature {row['Temperature (C)']} °C exceeds critical threshold",
                           "Action": "Stop equipment and inspect cooling system"})
        elif ts == "WARNING":
            alerts.append({"Level": "WARNING", "Category": "Equipment",
                           "Source": row["Equipment ID"],
                           "Message": f"Temperature {row['Temperature (C)']} °C approaching threshold",
                           "Action": "Schedule inspection"})
        if vs == "CRITICAL":
            alerts.append({"Level": "CRITICAL", "Category": "Equipment",
                           "Source": row["Equipment ID"],
                           "Message": f"Vibration {row['Vibration (mm/s)']} mm/s exceeds critical threshold",
                           "Action": "Inspect equipment and initiate appropriate maintenance/safety procedures"})
        elif vs == "WARNING":
            alerts.append({"Level": "WARNING", "Category": "Equipment",
                           "Source": row["Equipment ID"],
                           "Message": f"Vibration {row['Vibration (mm/s)']} mm/s approaching threshold",
                           "Action": "Monitor closely"})
        if row["Downtime"] > DOWNTIME_HIGH:
            alerts.append({"Level": "WARNING", "Category": "Maintenance",
                           "Source": row["Equipment ID"],
                           "Message": f"Excessive downtime: {row['Downtime']} h",
                           "Action": "Review maintenance plan"})
        if row["Availability (%)"] < AVAILABILITY_LOW:
            alerts.append({"Level": "WARNING", "Category": "Maintenance",
                           "Source": row["Equipment ID"],
                           "Message": f"Low availability: {row['Availability (%)']} %",
                           "Action": "Investigate root cause"})
        if row["Maintenance Status"] == "Overdue":
            alerts.append({"Level": "CRITICAL", "Category": "Maintenance",
                           "Source": row["Equipment ID"],
                           "Message": "Maintenance overdue",
                           "Action": "Schedule immediate maintenance"})

    for _, row in workers.iterrows():
        if row["PPE Compliance"] == "Non-Compliant":
            alerts.append({"Level": "WARNING", "Category": "Worker",
                           "Source": row["Worker ID"],
                           "Message": "PPE non-compliance recorded",
                           "Action": "Re-brief worker on PPE requirements"})
        if row["Fatigue Level"] >= FATIGUE_HIGH:
            alerts.append({"Level": "WARNING", "Category": "Worker",
                           "Source": row["Worker ID"],
                           "Message": f"High fatigue level ({row['Fatigue Level']}/10)",
                           "Action": "Consider shift rotation"})
        if row["Safety Training"] == "Expired":
            alerts.append({"Level": "WARNING", "Category": "Worker",
                           "Source": row["Worker ID"],
                           "Message": "Safety training expired",
                           "Action": "Schedule refresher training"})

    for _, row in incidents.iterrows():
        if row["Severity"] == "Critical" and row["Status"] != "Closed":
            alerts.append({"Level": "CRITICAL", "Category": "Safety",
                           "Source": row["Incident ID"],
                           "Message": f"Open critical incident at {row['Location']}",
                           "Action": "Escalate to Safety Manager"})

    if not alerts:
        return pd.DataFrame(columns=["Level", "Category", "Source", "Message", "Action"])
    return pd.DataFrame(alerts)


# =====================================================================
# SESSION / AUTH
# =====================================================================
def init_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.name = None
        st.session_state.page = "dashboard"
        st.session_state.show_welcome = False


def login_screen():
    st.markdown(
        "<h1 style='text-align:center;color:#1f4e79;'>⛏️ Khwezi Mining Monitor</h1>"
        "<p style='text-align:center;color:#666;'>Health, Safety & Equipment Monitoring</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("🔐 Sign in")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            users = load_users()
            u = users.get(username)
            if u and u["password"] == hash_pw(password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = u["role"]
                st.session_state.name = u["name"]
                st.session_state.page = "dashboard"
                st.session_state.show_welcome = True
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")


def welcome_screen():
    bg = get_bg_image_url()

    if bg:
        app_bg = f"linear-gradient(rgba(0,15,35,0.72), rgba(0,15,35,0.72)), url('{bg}')"
        bg_size = "cover, cover"
    else:
        app_bg = "linear-gradient(135deg, #1f4e79 0%, #0d2b48 100%)"
        bg_size = "cover"

    st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{display: none !important;}}
    [data-testid="collapsedControl"] {{display: none !important;}}
    header {{visibility: hidden;}}
    .stApp {{
        background: {app_bg};
        background-size: {bg_size};
        background-position: center;
        background-attachment: fixed;
    }}
    .welcome-title {{
        text-align: center;
        color: #ffffff;
        font-size: 3.2rem;
        font-weight: 800;
        text-shadow: 2px 2px 14px rgba(0,0,0,0.95);
        margin-bottom: 0.4rem;
        letter-spacing: 0.5px;
    }}
    .welcome-sub {{
        text-align: center;
        color: #e8eef5;
        font-size: 1.25rem;
        text-shadow: 1px 1px 8px rgba(0,0,0,0.9);
        margin-bottom: 0;
    }}
    div.stButton > button[kind="primary"],
    div.stButton > button[data-testid="baseButton-primary"] {{
        font-size: 1.15rem !important;
        padding: 0.9rem 2.2rem !important;
        border-radius: 12px !important;
        box-shadow: 0 6px 26px rgba(0,0,0,0.55) !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20vh;'></div>", unsafe_allow_html=True)

    st.markdown('<div class="welcome-title">⛏️ Welcome to Khwezi Mining Monitor</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="welcome-sub">Signed in as <b>{st.session_state.name}</b> &nbsp;·&nbsp; {st.session_state.role}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 6vh;'></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 1.4, 2])
    with c2:
        if st.button("🚀 Enter Dashboard", use_container_width=True, type="primary", key="welcome_enter_btn"):
            st.session_state.show_welcome = False
            st.session_state.page = "dashboard"
            st.rerun()


def has_permission(page: str) -> bool:
    return page in PERMISSIONS.get(st.session_state.role, [])


def require_permission(page: str):
    if not has_permission(page):
        st.error("🚫 You do not have permission to access this page.")
        st.stop()


# =====================================================================
# PAGES
# =====================================================================
def page_dashboard():
    st.title("📊 Mining Monitoring Dashboard")
    st.caption(f"Welcome, **{st.session_state.name}** — Role: *{st.session_state.role}*")

    workers = load_csv("workers.csv")
    incidents = load_csv("incidents.csv")
    equipment = load_csv("equipment.csv")
    alerts = build_alerts(workers, incidents, equipment)

    total_workers = len(workers)
    total_incidents = len(incidents)
    near_misses = int(workers["Near Misses"].sum())
    high_risk_obs = (workers["Risk Level"].isin(["High", "Critical"])).sum()
    ppe_comp = (workers["PPE Compliance"] == "Compliant").mean() * 100
    total_equip = len(equipment)
    equip_maint = (equipment["Maintenance Status"].isin(["Due", "Overdue", "Under Maintenance"])).sum()
    equip_alerts = len(alerts[alerts["Category"] == "Equipment"])
    avg_avail = equipment["Availability (%)"].mean()
    crit_alerts = (alerts["Level"] == "CRITICAL").sum()
    equip_available = (equipment["Maintenance Status"] == "Up to date").sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👷 Total Workers", total_workers)
    c2.metric("🚨 Safety Incidents", total_incidents)
    c3.metric("⚠️ Near Misses", near_misses)
    c4.metric("🔥 High-Risk Observations", int(high_risk_obs))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🦺 PPE Compliance", f"{ppe_comp:.1f} %")
    c2.metric("🚜 Total Equipment", total_equip)
    c3.metric("✅ Equipment Available", int(equip_available))
    c4.metric("🔧 Under Maintenance", int(equip_maint))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔔 Equipment Alerts", equip_alerts)
    c2.metric("📉 Avg Availability", f"{avg_avail:.1f} %")
    c3.metric("🛑 Critical Alerts", int(crit_alerts))
    c4.metric("📅 Today", datetime.now().strftime("%d %b %Y"))

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Incidents by Department")
        by_dept = incidents.groupby("Department").size().reset_index(name="Count")
        fig = px.bar(by_dept, x="Department", y="Count", color="Department",
                     color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Incidents by Severity")
        by_sev = incidents.groupby("Severity").size().reset_index(name="Count")
        fig = px.pie(by_sev, names="Severity", values="Count", hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Equipment Status Distribution")
        st_data = equipment["Maintenance Status"].value_counts().reset_index()
        st_data.columns = ["Status", "Count"]
        fig = px.bar(st_data, x="Status", y="Count", color="Status")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Average Availability by Equipment Type")
        av = equipment.groupby("Equipment Type")["Availability (%)"].mean().reset_index()
        fig = px.bar(av, x="Equipment Type", y="Availability (%)", color="Equipment Type")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔔 Latest Active Alerts")
    if alerts.empty:
        st.success("No active alerts.")
    else:
        critical = alerts[alerts["Level"] == "CRITICAL"].head(5)
        for _, a in critical.iterrows():
            st.error(
                f"**[{a['Level']}] {a['Category']} — {a['Source']}**\n\n"
                f"{a['Message']}\n\n**Recommended Action:** {a['Action']}"
            )
        st.dataframe(alerts.head(20), use_container_width=True)


def page_workers():
    st.title("👷 Worker Health & Safety Monitoring")
    require_permission("workers")

    workers = load_csv("workers.csv")

    st.subheader("Filters")
    c1, c2, c3 = st.columns(3)
    dept = c1.multiselect("Department", sorted(workers["Department"].unique()))
    shift = c2.multiselect("Shift", sorted(workers["Shift"].unique()))
    risk = c3.multiselect("Risk Level", ["Low", "Medium", "High", "Critical"])

    df = workers.copy()
    if dept:
        df = df[df["Department"].isin(dept)]
    if shift:
        df = df[df["Shift"].isin(shift)]
    if risk:
        df = df[df["Risk Level"].isin(risk)]

    st.metric("Workers shown", len(df))
    st.dataframe(df, use_container_width=True)

    st.divider()
    st.subheader("⚠️ Unsafe Conditions")
    unsafe = workers[
        (workers["PPE Compliance"] == "Non-Compliant") |
        (workers["Safety Training"] == "Expired") |
        (workers["Fatigue Level"] >= FATIGUE_HIGH)
    ]
    if unsafe.empty:
        st.success("No unsafe conditions detected.")
    else:
        st.warning(f"{len(unsafe)} worker(s) flagged for unsafe conditions.")
        st.dataframe(unsafe, use_container_width=True)


def page_incidents():
    st.title("🚨 Safety Incident Database")
    require_permission("incidents")

    incidents = load_csv("incidents.csv")

    tab1, tab2, tab3 = st.tabs(["📋 View / Filter", "➕ Add Incident", "📈 Trends"])

    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        dept = c1.multiselect("Department", sorted(incidents["Department"].unique()))
        shift = c2.multiselect("Shift", ["Day", "Night"])
        sev = c3.multiselect("Severity", sorted(incidents["Severity"].unique()))
        status = c4.multiselect("Status", sorted(incidents["Status"].unique()))

        search = st.text_input("🔍 Search (ID, location, type, cause)")

        df = incidents.copy()
        if dept: df = df[df["Department"].isin(dept)]
        if shift: df = df[df["Shift"].isin(shift)]
        if sev: df = df[df["Severity"].isin(sev)]
        if status: df = df[df["Status"].isin(status)]
        if search:
            mask = df.apply(lambda r: search.lower() in str(r.values).lower(), axis=1)
            df = df[mask]

        st.metric("Incidents shown", len(df))
        st.dataframe(df, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("High/Critical", (df["Severity"].isin(["Major", "Critical"])).sum())
        c2.metric("With Injury", (df["Injury"] == "Yes").sum())
        c3.metric("Lost-Time Injuries", (df["Lost-Time Injury"] == "Yes").sum())

    with tab2:
        with st.form("add_incident"):
            st.subheader("Record New Incident")
            c1, c2, c3 = st.columns(3)
            date = c1.date_input("Date", datetime.now())
            time = c2.time_input("Time", datetime.now().time())
            shift = c3.selectbox("Shift", ["Day", "Night"])
            c1, c2, c3 = st.columns(3)
            location = c1.text_input("Location")
            department = c2.selectbox("Department", ["Underground", "Open Pit", "Processing", "Maintenance", "Engineering"])
            itype = c3.selectbox("Incident Type", ["Slip/Fall", "Equipment Failure", "Struck by Object",
                                                    "Caught In/Between", "Chemical Exposure", "Electrical", "Fire", "Other"])
            c1, c2, c3 = st.columns(3)
            severity = c1.selectbox("Severity", ["Minor", "Moderate", "Major", "Critical"])
            injury = c2.selectbox("Injury", ["No", "Yes"])
            lti = c3.selectbox("Lost-Time Injury", ["No", "Yes"])
            cause = st.text_input("Cause")
            corrective = st.text_input("Corrective Action", "Pending")
            status = st.selectbox("Status", ["Open", "In Progress", "Closed"])

            if st.form_submit_button("Save Incident"):
                new_id = f"INC-{len(incidents) + 1:04d}"
                new_row = pd.DataFrame([{
                    "Incident ID": new_id,
                    "Date": date.strftime("%Y-%m-%d"),
                    "Time": time.strftime("%H:%M"),
                    "Shift": shift,
                    "Location": location,
                    "Department": department,
                    "Incident Type": itype,
                    "Severity": severity,
                    "Injury": injury,
                    "Lost-Time Injury": lti,
                    "Cause": cause,
                    "Corrective Action": corrective,
                    "Status": status,
                }])
                incidents = pd.concat([incidents, new_row], ignore_index=True)
                incidents.to_csv(os.path.join(DATA_DIR, "incidents.csv"), index=False)
                st.cache_data.clear()
                st.success(f"Incident {new_id} recorded.")
                st.rerun()

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            by_type = incidents.groupby("Incident Type").size().reset_index(name="Count")
            fig = px.bar(by_type.sort_values("Count"), x="Count", y="Incident Type",
                         orientation="h", color="Incident Type")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            incidents["Date"] = pd.to_datetime(incidents["Date"])
            monthly = incidents.groupby(incidents["Date"].dt.to_period("M")).size().reset_index(name="Count")
            monthly["Date"] = monthly["Date"].astype(str)
            fig = px.line(monthly, x="Date", y="Count", markers=True, title="Incidents per Month")
            st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            by_shift = incidents.groupby("Shift").size().reset_index(name="Count")
            fig = px.pie(by_shift, names="Shift", values="Count", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            by_cause = incidents.groupby("Cause").size().reset_index(name="Count").sort_values("Count")
            fig = px.bar(by_cause, x="Count", y="Cause", orientation="h")
            st.plotly_chart(fig, use_container_width=True)


def page_equipment():
    st.title("🚜 Equipment Database")
    require_permission("equipment")

    equipment = load_csv("equipment.csv")

    c1, c2, c3 = st.columns(3)
    etype = c1.multiselect("Equipment Type", sorted(equipment["Equipment Type"].unique()))
    manu = c2.multiselect("Manufacturer", sorted(equipment["Manufacturer"].unique()))
    status = c3.multiselect("Maintenance Status", sorted(equipment["Maintenance Status"].unique()))

    df = equipment.copy()
    if etype: df = df[df["Equipment Type"].isin(etype)]
    if manu: df = df[df["Manufacturer"].isin(manu)]
    if status: df = df[df["Maintenance Status"].isin(status)]

    st.metric("Equipment shown", len(df))
    st.dataframe(df, use_container_width=True)

    st.divider()
    st.subheader("➕ Add Equipment")
    with st.form("add_equip"):
        c1, c2, c3 = st.columns(3)
        eid = c1.text_input("Equipment ID (e.g. TRK-099)")
        etype_in = c2.selectbox("Equipment Type", ["Haul Truck", "Loader", "Excavator", "Drill",
                                                    "Bulldozer", "Scraper Winch", "Crusher", "Conveyor"])
        manu_in = c3.selectbox("Manufacturer", ["Caterpillar", "Komatsu", "Hitachi", "Sandvik", "Atlas Copco", "Joy Global"])
        c1, c2, c3 = st.columns(3)
        op = c1.number_input("Operating Hours", 0, 20000, 2000)
        dt = c2.number_input("Downtime (h)", 0, 5000, 100)
        temp = c3.number_input("Temperature (°C)", 0.0, 200.0, 70.0)
        c1, c2, c3 = st.columns(3)
        vib = c1.number_input("Vibration (mm/s)", 0.0, 30.0, 3.0)
        fuel = c2.number_input("Fuel Consumption (L/h)", 0.0, 100.0, 20.0)
        mstatus = c3.selectbox("Maintenance Status", ["Up to date", "Due", "Overdue", "Under Maintenance"])

        if st.form_submit_button("Save Equipment"):
            avail = op / (op + dt) * 100 if (op + dt) > 0 else 0
            new = pd.DataFrame([{
                "Equipment ID": eid, "Equipment Type": etype_in, "Manufacturer": manu_in,
                "Operating Hours": op, "Downtime": dt,
                "Temperature (C)": temp, "Vibration (mm/s)": vib,
                "Fuel Consumption (L/h)": fuel,
                "Brake Status": "OK", "Tyre Status": "OK", "Engine Status": "OK",
                "Maintenance Status": mstatus, "Availability (%)": round(avail, 1),
            }])
            equipment = pd.concat([equipment, new], ignore_index=True)
            equipment.to_csv(os.path.join(DATA_DIR, "equipment.csv"), index=False)
            st.cache_data.clear()
            st.success(f"Equipment {eid} added.")
            st.rerun()


def page_condition():
    st.title("🌡️ Equipment Condition Monitoring")
    require_permission("condition")

    equipment = load_csv("equipment.csv")
    equipment["Temp Status"] = equipment["Temperature (C)"].apply(temp_status)
    equipment["Vib Status"] = equipment["Vibration (mm/s)"].apply(vib_status)
    equipment["Overall"] = equipment.apply(overall_status, axis=1)

    st.info("ℹ️ Thresholds below are educational prototype values only, not manufacturer limits.")
    st.markdown(
        f"**Temperature:** Normal < {TEMP_WARNING} °C · Warning {TEMP_WARNING}–{TEMP_CRITICAL} °C · "
        f"Critical > {TEMP_CRITICAL} °C  \n"
        f"**Vibration:** Normal < {VIB_WARNING} mm/s · Warning {VIB_WARNING}–{VIB_CRITICAL} mm/s · "
        f"Critical > {VIB_CRITICAL} mm/s"
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("🟢 NORMAL", (equipment["Overall"] == "NORMAL").sum())
    c2.metric("🟡 WARNING", (equipment["Overall"] == "WARNING").sum())
    c3.metric("🔴 CRITICAL", (equipment["Overall"] == "CRITICAL").sum())

    st.dataframe(
        equipment[["Equipment ID", "Equipment Type", "Temperature (C)", "Temp Status",
                   "Vibration (mm/s)", "Vib Status", "Overall"]],
        use_container_width=True,
    )

    st.subheader("Critical Equipment")
    crit = equipment[equipment["Overall"] == "CRITICAL"]
    if crit.empty:
        st.success("No critical equipment.")
    else:
        for _, r in crit.iterrows():
            st.error(
                f"**MINING MONITORING ALERT — [CRITICAL]**  \n"
                f"Equipment ID: `{r['Equipment ID']}`  \n"
                f"Temperature: {r['Temperature (C)']} °C | Vibration: {r['Vibration (mm/s)']} mm/s  \n"
                f"**Recommended Action:** Inspect equipment and initiate appropriate maintenance/safety procedures."
            )


def page_maintenance():
    st.title("🔧 Equipment Maintenance Monitoring")
    require_permission("maintenance")

    equipment = load_csv("equipment.csv")
    equipment["Availability (%)"] = (equipment["Operating Hours"] /
                                     (equipment["Operating Hours"] + equipment["Downtime"]) * 100).round(1)

    st.subheader("Filter")
    c1, c2 = st.columns(2)
    status = c1.multiselect("Maintenance Status", sorted(equipment["Maintenance Status"].unique()))
    show_low = c2.checkbox("Only low availability (< 80%)", value=False)

    df = equipment.copy()
    if status:
        df = df[df["Maintenance Status"].isin(status)]
    if show_low:
        df = df[df["Availability (%)"] < AVAILABILITY_LOW]

    st.metric("Equipment shown", len(df))
    st.dataframe(
        df[["Equipment ID", "Equipment Type", "Operating Hours", "Downtime",
            "Availability (%)", "Maintenance Status"]],
        use_container_width=True,
    )

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Due for Maintenance", (equipment["Maintenance Status"] == "Due").sum())
    c2.metric("Overdue", (equipment["Maintenance Status"] == "Overdue").sum())
    c3.metric("Under Maintenance", (equipment["Maintenance Status"] == "Under Maintenance").sum())

    st.subheader("Priority Maintenance List")
    priority = equipment[
        (equipment["Maintenance Status"].isin(["Overdue", "Due"])) |
        (equipment["Availability (%)"] < AVAILABILITY_LOW) |
        (equipment["Downtime"] > DOWNTIME_HIGH)
    ].sort_values("Availability (%)")
    st.dataframe(priority, use_container_width=True)

    st.subheader("Availability by Equipment Type")
    fig = px.box(equipment, x="Equipment Type", y="Availability (%)", color="Equipment Type")
    st.plotly_chart(fig, use_container_width=True)


def page_risk():
    st.title("⚠️ Risk Assessment")
    require_permission("risk")

    st.markdown("**Risk Score = Likelihood × Consequence** (both on a 1–5 scale)")

    c1, c2 = st.columns(2)
    likelihood = c1.slider("Likelihood", 1, 5, 3)
    consequence = c2.slider("Consequence", 1, 5, 3)

    score = likelihood * consequence
    classification = risk_classification(score)

    c1, c2, c3 = st.columns(3)
    c1.metric("Risk Score", score)
    c2.metric("Classification", classification)
    if classification == "Critical":
        c3.error("🚨 CRITICAL — Immediate intervention required")
    elif classification == "High":
        c3.warning("⚠️ HIGH — Action required soon")
    elif classification == "Medium":
        c3.info("ℹ️ MEDIUM — Monitor")
    else:
        c3.success("✅ LOW — Acceptable")

    st.divider()

    st.subheader("Risk Matrix")
    matrix = pd.DataFrame(
        [[likelihood * consequence for consequence in range(1, 6)] for likelihood in range(5, 0, -1)],
        index=[f"L{l}" for l in range(5, 0, -1)],
        columns=[f"C{c}" for c in range(1, 6)],
    )
    st.dataframe(matrix.style.background_gradient(cmap="RdYlGn_r"), use_container_width=True)

    st.divider()
    st.subheader("Add Safety Observation Risk")
    with st.form("risk_form"):
        worker = st.text_input("Worker ID")
        desc = st.text_area("Observation description")
        lk = st.slider("Likelihood (1–5)", 1, 5, 3, key="lk")
        cs = st.slider("Consequence (1–5)", 1, 5, 3, key="cs")
        if st.form_submit_button("Save Risk"):
            sc = lk * cs
            cl = risk_classification(sc)
            st.success(f"Observation saved. Score = {sc} → {cl}")
            if cl in ("High", "Critical"):
                st.error(f"🚨 {cl} risk recorded — notify supervisor immediately.")


def page_alerts():
    st.title("🔔 Alerts & Notifications")
    require_permission("alerts")

    workers = load_csv("workers.csv")
    incidents = load_csv("incidents.csv")
    equipment = load_csv("equipment.csv")
    alerts = build_alerts(workers, incidents, equipment)

    if alerts.empty:
        st.success("No active alerts.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("🔴 Critical", (alerts["Level"] == "CRITICAL").sum())
    c2.metric("🟡 Warning", (alerts["Level"] == "WARNING").sum())
    c3.metric("Total", len(alerts))

    level_filter = st.multiselect("Filter by level", ["CRITICAL", "WARNING"], default=["CRITICAL", "WARNING"])
    cat_filter = st.multiselect("Filter by category", sorted(alerts["Category"].unique()),
                                default=sorted(alerts["Category"].unique()))

    df = alerts[alerts["Level"].isin(level_filter) & alerts["Category"].isin(cat_filter)]

    for _, a in df.iterrows():
        msg = f"**[{a['Level']}] {a['Category']} — {a['Source']}**\n\n{a['Message']}\n\n**Recommended Action:** {a['Action']}"
        if a["Level"] == "CRITICAL":
            st.error(msg)
        else:
            st.warning(msg)


def page_analytics():
    st.title("📈 Interactive Data Analysis")
    require_permission("analytics")

    workers = load_csv("workers.csv")
    incidents = load_csv("incidents.csv")
    equipment = load_csv("equipment.csv")

    incidents["Date"] = pd.to_datetime(incidents["Date"])

    st.subheader("🔎 Business Question Explorer")
    question = st.selectbox("Choose a question", [
        "How many safety incidents occurred in the selected period?",
        "Which department has the highest number of incidents?",
        "Which shift records the most incidents?",
        "What percentage of workers comply with PPE?",
        "How many near misses have been recorded?",
        "Which incident types occur most frequently?",
        "How many incidents are classified as high or critical?",
        "Which equipment has the highest downtime?",
        "Which equipment has the lowest availability?",
        "Which equipment has the highest vibration?",
        "Which equipment has the highest operating temperature?",
        "Which equipment requires maintenance?",
        "Which equipment is overdue for maintenance?",
        "What is the average equipment availability?",
        "Are safety incidents associated with particular shifts?",
    ])

    st.divider()

    if question == "How many safety incidents occurred in the selected period?":
        c1, c2 = st.columns(2)
        start = c1.date_input("From", incidents["Date"].min().date())
        end = c2.date_input("To", incidents["Date"].max().date())
        mask = (incidents["Date"] >= pd.to_datetime(start)) & (incidents["Date"] <= pd.to_datetime(end))
        st.metric("Incidents in period", int(mask.sum()))

    elif question == "Which department has the highest number of incidents?":
        d = incidents.groupby("Department").size().reset_index(name="Count").sort_values("Count", ascending=False)
        st.dataframe(d, use_container_width=True)
        st.plotly_chart(px.bar(d, x="Department", y="Count", color="Department"), use_container_width=True)

    elif question == "Which shift records the most incidents?":
        d = incidents.groupby("Shift").size().reset_index(name="Count")
        st.dataframe(d, use_container_width=True)
        st.plotly_chart(px.bar(d, x="Shift", y="Count", color="Shift"), use_container_width=True)

    elif question == "What percentage of workers comply with PPE?":
        pct = (workers["PPE Compliance"] == "Compliant").mean() * 100
        st.metric("PPE Compliance", f"{pct:.1f} %")
        d = workers["PPE Compliance"].value_counts().reset_index()
        d.columns = ["Status", "Count"]
        st.plotly_chart(px.pie(d, names="Status", values="Count", hole=0.4), use_container_width=True)

    elif question == "How many near misses have been recorded?":
        st.metric("Total Near Misses", int(workers["Near Misses"].sum()))
        d = workers.groupby("Department")["Near Misses"].sum().reset_index()
        st.plotly_chart(px.bar(d, x="Department", y="Near Misses", color="Department"), use_container_width=True)

    elif question == "Which incident types occur most frequently?":
        d = incidents.groupby("Incident Type").size().reset_index(name="Count").sort_values("Count", ascending=False)
        st.dataframe(d, use_container_width=True)
        st.plotly_chart(px.bar(d, x="Count", y="Incident Type", orientation="h"), use_container_width=True)

    elif question == "How many incidents are classified as high or critical?":
        c = incidents["Severity"].isin(["Major", "Critical"]).sum()
        st.metric("High/Critical incidents", int(c))
        d = incidents.groupby("Severity").size().reset_index(name="Count")
        st.plotly_chart(px.bar(d, x="Severity", y="Count", color="Severity"), use_container_width=True)

    elif question == "Which equipment has the highest downtime?":
        d = equipment.nlargest(10, "Downtime")[["Equipment ID", "Equipment Type", "Downtime"]]
        st.dataframe(d, use_container_width=True)
        st.plotly_chart(px.bar(d, x="Downtime", y="Equipment ID", orientation="h"), use_container_width=True)

    elif question == "Which equipment has the lowest availability?":
        d = equipment.nsmallest(10, "Availability (%)")[["Equipment ID", "Equipment Type", "Availability (%)"]]
        st.dataframe(d, use_container_width=True)
        st.plotly_chart(px.bar(d, x="Availability (%)", y="Equipment ID", orientation="h"), use_container_width=True)

    elif question == "Which equipment has the highest vibration?":
        d = equipment.nlargest(10, "Vibration (mm/s)")[["Equipment ID", "Equipment Type", "Vibration (mm/s)"]]
        st.dataframe(d, use_container_width=True)
        st.plotly_chart(px.bar(d, x="Vibration (mm/s)", y="Equipment ID", orientation="h"), use_container_width=True)

    elif question == "Which equipment has the highest operating temperature?":
        d = equipment.nlargest(10, "Temperature (C)")[["Equipment ID", "Equipment Type", "Temperature (C)"]]
        st.dataframe(d, use_container_width=True)
        st.plotly_chart(px.bar(d, x="Temperature (C)", y="Equipment ID", orientation="h"), use_container_width=True)

    elif question == "Which equipment requires maintenance?":
        d = equipment[equipment["Maintenance Status"].isin(["Due", "Overdue"])]
        st.metric("Requires maintenance", len(d))
        st.dataframe(d, use_container_width=True)

    elif question == "Which equipment is overdue for maintenance?":
        d = equipment[equipment["Maintenance Status"] == "Overdue"]
        st.metric("Overdue", len(d))
        st.dataframe(d, use_container_width=True)

    elif question == "What is the average equipment availability?":
        st.metric("Average availability", f"{equipment['Availability (%)'].mean():.1f} %")
        d = equipment.groupby("Equipment Type")["Availability (%)"].mean().reset_index()
        st.plotly_chart(px.bar(d, x="Equipment Type", y="Availability (%)", color="Equipment Type"), use_container_width=True)

    elif question == "Are safety incidents associated with particular shifts?":
        d = incidents.groupby(["Shift", "Severity"]).size().reset_index(name="Count")
        st.plotly_chart(px.bar(d, x="Shift", y="Count", color="Severity", barmode="group"), use_container_width=True)
        st.dataframe(d, use_container_width=True)


def page_reports():
    st.title("📄 Reports")
    require_permission("reports")

    workers = load_csv("workers.csv")
    incidents = load_csv("incidents.csv")
    equipment = load_csv("equipment.csv")

    st.subheader("Generate Summary Report")
    if st.button("📥 Build Report"):
        ppe = (workers["PPE Compliance"] == "Compliant").mean() * 100
        st.markdown(f"""
### Khwezi Mining — Summary Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

#### Workforce
- Total workers: **{len(workers)}**
- PPE compliance: **{ppe:.1f} %**
- High/Critical risk workers: **{(workers['Risk Level'].isin(['High', 'Critical'])).sum()}**

#### Safety
- Total incidents: **{len(incidents)}**
- Major/Critical incidents: **{(incidents['Severity'].isin(['Major', 'Critical'])).sum()}**
- Lost-time injuries: **{(incidents['Lost-Time Injury'] == 'Yes').sum()}**

#### Equipment
- Total equipment: **{len(equipment)}**
- Average availability: **{equipment['Availability (%)'].mean():.1f} %**
- Overdue maintenance: **{(equipment['Maintenance Status'] == 'Overdue').sum()}**

---
*This is a prototype report for MINN2020A.*
        """)

    st.divider()
    st.subheader("Export Data")
    c1, c2, c3 = st.columns(3)
    c1.download_button("⬇️ Workers CSV", workers.to_csv(index=False), "workers_export.csv")
    c2.download_button("⬇️ Incidents CSV", incidents.to_csv(index=False), "incidents_export.csv")
    c3.download_button("⬇️ Equipment CSV", equipment.to_csv(index=False), "equipment_export.csv")


def page_users():
    st.title("👥 Manage Users")
    require_permission("users")

    users = load_users()

    st.subheader("Existing Users")
    rows = [{"Username": u, "Name": d["name"], "Role": d["role"]} for u, d in users.items()]
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    st.divider()
    st.subheader("Add New User")
    with st.form("add_user"):
        c1, c2 = st.columns(2)
        un = c1.text_input("Username")
        nm = c2.text_input("Full Name")
        pw = c1.text_input("Password", type="password")
        rl = c2.selectbox("Role", list(PERMISSIONS.keys()))
        if st.form_submit_button("Create User"):
            if un in users:
                st.error("Username already exists.")
            elif not un or not pw:
                st.error("Username and password required.")
            else:
                users[un] = {"password": hash_pw(pw), "role": rl, "name": nm}
                save_users(users)
                st.success(f"User {un} created with role {rl}.")
                st.rerun()


# =====================================================================
# MAIN
# =====================================================================
def main():
    generate_data()
    init_session()

    if not st.session_state.logged_in:
        login_screen()
        return

    if st.session_state.get("show_welcome", False):
        welcome_screen()
        return

    with st.sidebar:
        st.markdown(f"### ⛏️ Khwezi Monitor")
        st.markdown(f"👤 **{st.session_state.name}**  \n`{st.session_state.role}`")
        st.divider()

        allowed = PERMISSIONS.get(st.session_state.role, [])
        choice = st.radio(
            "Navigation",
            options=allowed,
            format_func=lambda k: PAGES[k],
            index=allowed.index(st.session_state.page) if st.session_state.page in allowed else 0,
        )
        st.session_state.page = choice

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            for k in ["logged_in", "username", "role", "name", "page", "show_welcome"]:
                st.session_state.pop(k, None)
            st.rerun()

    page = st.session_state.page
    if not has_permission(page):
        st.error("🚫 Access denied.")
        return

    routes = {
        "dashboard":   page_dashboard,
        "workers":     page_workers,
        "incidents":   page_incidents,
        "equipment":   page_equipment,
        "condition":   page_condition,
        "maintenance": page_maintenance,
        "risk":        page_risk,
        "alerts":      page_alerts,
        "analytics":   page_analytics,
        "reports":     page_reports,
        "users":       page_users,
    }
    routes[page]()


if __name__ == "__main__":
    main()