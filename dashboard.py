import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import random
from datetime import datetime
import random
import pandas as pd
# -----------------------------
# Basic page config (title, icon, theme)
# -----------------------------
st.set_page_config(
    page_title="Smart Home Network Security Dashboard",
    page_icon="🔐",
    layout="wide"
)

st.markdown(
    """
    <style>
    .main {
        background-color: #111827;
        color: #F9FAFB;
    }
    .stButton>button {
        border-radius: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Data helpers (JSON storage)
# -----------------------------
DATA_FILE = "data/network.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"devices": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()
devices = data.get("devices", [])

# Convert to DataFrame for easier use
devices_df = pd.DataFrame(devices)

# -----------------------------
# Session state (for alerts)
# -----------------------------
if "alerts" not in st.session_state:
    # Initial alert list (static + good defaults)
    st.session_state.alerts = [
        {
            "time": "10:00",
            "source": "Guest Phone",
            "destination": "Admin PC",
            "type": "Unauthorized Access",
            "status": "Blocked"
        },
        {
            "time": "10:05",
            "source": "IoT Camera",
            "destination": "User Laptop",
            "type": "Cross-VLAN Attempt",
            "status": "Blocked"
        },
        {
            "time": "10:10",
            "source": "Smart Bulb",
            "destination": "Admin PC",
            "type": "ARP Spoofing Attempt",
            "status": "Suspicious"
        },
        {
            "time": "10:20",
            "source": "Guest Phone",
            "destination": "Admin PC",
            "type": "Unauthorized Access",
            "status": "Blocked"
        }
    ]

alerts = st.session_state.alerts

# -----------------------------
# Sidebar navigation
# -----------------------------
with st.sidebar:
    st.header("🔐 Navigation")
    page = st.radio(
        "Go to:",
        ["Dashboard", "Alerts", "Devices", "Quarantine Center", "Network Overview"]
    )

# -----------------------------
# Helper functions for device actions
# -----------------------------
def update_device_status(name, new_status, new_vlan=None):
    changed = False
    for d in devices:
        if d["name"] == name:
            d["status"] = new_status
            if new_vlan is not None:
                d["vlan"] = new_vlan
            changed = True
            break
    if changed:
        save_data({"devices": devices})

def count_quarantined():
    return sum(1 for d in devices if d["status"] == "Quarantined")

def count_active():
    return len(devices)

# -----------------------------
# DASHBOARD PAGE
# -----------------------------
if page == "Dashboard":
    st.title("🏠 Smart Home Network Security Dashboard")
    st.caption("Monitor home IoT devices, VLAN segmentation, alerts and intrusions in real time.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Active Devices", count_active())

    with col2:
        st.metric("Blocked Attacks", len(alerts))

    with col3:
        st.metric("Quarantined Devices", count_quarantined())

    st.markdown("---")
    st.subheader("🖥️ Connected Devices")

    if not devices_df.empty:
        st.table(devices_df)
    else:
        st.info("No device data available yet.")

# -----------------------------
# ALERTS PAGE
# -----------------------------
elif page == "Alerts":
    st.title("🚨 Security Alerts")

    if alerts:
        st.table(pd.DataFrame(alerts))
    else:
        st.success("No alerts generated yet.")

    st.markdown("### Simulate Attack 🧪")
    st.caption("Generate a new random attack event for demonstration.")

    if st.button("🔴 Generate Attack Event"):
        possible_sources = [d["name"] for d in devices]
        possible_destinations = ["Admin PC", "User Laptop", "Home Server"]
        attack_types = [
            "Unauthorized Access",
            "Cross-VLAN Attempt",
            "Port Scan",
            "Brute-Force Login",
            "Suspicious Traffic"
        ]
        outcomes = ["Blocked", "Quarantined", "Suspicious"]

        src = random.choice(possible_sources) if possible_sources else "Unknown Device"
        dst = random.choice(possible_destinations)
        atype = random.choice(attack_types)
        outcome = random.choice(outcomes)

        now = datetime.now().strftime("%H:%M:%S")

        st.session_state.alerts.append(
            {
                "time": now,
                "source": src,
                "destination": dst,
                "type": atype,
                "status": outcome
            }
        )

        st.success(f"New alert generated: {src} → {dst} ({atype}, {outcome})")

    # Show updated table
    if st.session_state.alerts:
        st.markdown("### Live Alert Log")
        st.dataframe(pd.DataFrame(st.session_state.alerts), use_container_width=True)

# -----------------------------
# DEVICES PAGE (Device Explorer with actions)
# -----------------------------
elif page == "Devices":
    st.title("💻 Device Explorer")
    st.caption("View device details and take actions.")

    if not devices:
        st.info("No devices available.")
    else:
        for d in devices:
            with st.expander(f"{d['name']} — {d['ip']} (VLAN {d['vlan']})", expanded=False):
                st.write(f"**Status:** {d['status']}")
                st.write(f"**VLAN:** {d['vlan']}")

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if st.button(f"Mark Safe ({d['name']})", key=f"safe_{d['name']}"):
                        update_device_status(d["name"], "Safe")
                        st.success(f"{d['name']} marked as Safe. Refresh page to see updates.")

                with col_b:
                    if st.button(f"Block ({d['name']})", key=f"block_{d['name']}"):
                        update_device_status(d["name"], "Suspicious")
                        st.warning(f"{d['name']} marked as Suspicious. Refresh page to see updates.")

                with col_c:
                    if st.button(f"Isolate ({d['name']})", key=f"iso_{d['name']}"):
                        update_device_status(d["name"], "Quarantined", new_vlan=99)
                        st.error(f"{d['name']} moved to Quarantine VLAN 99. Refresh page to see updates.")

# -----------------------------
# QUARANTINE CENTER
# -----------------------------
elif page == "Quarantine Center":
    st.title("🚫 Quarantine Center")

    quarantined = [d for d in devices if d["status"] == "Quarantined"]

    if quarantined:
        q_df = pd.DataFrame(quarantined)
        st.table(q_df)

        st.markdown("### Release Devices from Quarantine")
        for d in quarantined:
            if st.button(f"Release {d['name']}", key=f"rel_{d['name']}"):
                update_device_status(d["name"], "Safe", new_vlan=40 if d["vlan"] == 99 else d["vlan"])
                st.success(f"{d['name']} released from Quarantine. Refresh page to see updates.")
    else:
        st.success("No devices in quarantine! 🎉")

# -----------------------------
# NETWORK OVERVIEW (Charts)
# -----------------------------

elif page == "Network Overview":
    st.title("🌐 Network Overview")

    st.write("""
    - VLAN 10 ➜ Admin  
    - VLAN 20 ➜ Users  
    - VLAN 30 ➜ Guest  
    - VLAN 40 ➜ IoT  
    - VLAN 99 ➜ Quarantine  
    """)

    # Generate dynamic simulated alert data
    alerts_data = pd.DataFrame({
        "time": ["10:00", "10:05", "10:10", "10:15", "10:20"],
        "alerts": [random.randint(0, 12) for _ in range(5)]
    })

    # Device distribution chart
    df = pd.DataFrame(devices)
    vlan_counts = df["vlan"].value_counts().sort_index()
    st.subheader("📊 Device Distribution by VLAN")
    st.bar_chart(vlan_counts)

    # Device security status (pie chart)
    status_counts = df["status"].value_counts()
    st.subheader("🛡️ Device Security Status")

    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="Security Status of Devices"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Alerts over time (dynamic)
    st.subheader("📈 Alerts Over Time (Simulated)")

    line_chart = px.line(
        alerts_data,
        x="time",
        y="alerts",
        title="Alert Activity Over Time",
        markers=True
    )
    st.plotly_chart(line_chart, use_container_width=True)
