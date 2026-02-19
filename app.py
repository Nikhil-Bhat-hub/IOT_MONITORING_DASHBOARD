import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
from datetime import datetime
import os

st.set_page_config(layout="wide")

# ============================
# IMPORTANT: CHANGE THIS AFTER BACKEND DEPLOY
# ============================
API_BASE = "https://iot-monitoring-dashboard-yru1.onrender.com"

API_LOGIN = f"{API_BASE}/login/"
API_GET = f"{API_BASE}/get_devices/"
API_ANALYTICS = f"{API_BASE}/analytics/"
API_UPDATE = f"{API_BASE}/update_device/"
API_HISTORY = f"{API_BASE}/history/"
API_ACTIVE_USERS = f"{API_BASE}/active_users/"

# ---------------- LOGIN ----------------
if "session_id" not in st.session_state:

    st.title("🔐 Enterprise IoT Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            res = requests.post(API_LOGIN, json={
                "username": username,
                "password": password
            }).json()

            if res.get("success"):
                st.session_state.session_id = res["session_id"]
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid Credentials")
        except:
            st.error("Backend not reachable. Check API URL.")

    st.stop()

device_id = st.session_state.username

st.title("🚀 Enterprise IoT Monitoring Dashboard")

# ---------------- AUTO REFRESH ----------------
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()

if (datetime.now() - st.session_state.last_refresh).seconds > 5:
    st.session_state.last_refresh = datetime.now()
    st.rerun()

# ---------------- GPS UPDATE ----------------
components.html(f"""
<script>
function sendLocation() {{
    if (navigator.geolocation) {{
        navigator.geolocation.getCurrentPosition(function(position) {{
            fetch("{API_UPDATE}?device_id={device_id}" +
                  "&latitude=" + position.coords.latitude +
                  "&longitude=" + position.coords.longitude +
                  "&signal=" + Math.floor(Math.random()*100) +
                  "&data_usage=" + (Math.random()*5).toFixed(2) +
                  "&active_duration=10", {{
                method: "POST"
            }});
        }});
    }}
}}
setInterval(sendLocation, 5000);
sendLocation();
</script>
""", height=0)

# ---------------- FETCH DATA ----------------
try:
    devices = requests.get(API_GET).json()
    analytics = requests.get(API_ANALYTICS).json()
    active_users = requests.get(API_ACTIVE_USERS).json()["active_users"]
except:
    st.error("Backend connection failed.")
    st.stop()

df = pd.DataFrame(devices)

# ---------------- KPI ----------------
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Devices", analytics["total_devices"])
col2.metric("Online", analytics["online_devices"])
col3.metric("Offline", analytics["offline_devices"])
col4.metric("Avg Signal", analytics["average_signal_strength"])
col5.metric("Active Users", active_users)

st.divider()

if not df.empty:

    st.subheader("🌍 Live Device Map")
    map_df = df.rename(columns={"latitude": "lat", "longitude": "lon"})
    st.map(map_df)

    st.divider()

    selected_device = st.selectbox(
        "Select Device",
        df["device_id"].unique(),
        key="device_selector"
    )

    device = df[df["device_id"] == selected_device].iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Status", device["status"])
    c2.metric("Signal", device["signal"])
    c3.metric("Data Usage", device["data_usage"])

    if device["signal"] < 30:
        st.error("🚨 Signal Strength Low")

    history = requests.get(API_HISTORY + selected_device).json()
    hist_df = pd.DataFrame(history)

    if not hist_df.empty:
        hist_df = hist_df.sort_values("timestamp")

        st.subheader("🔴 Signal Trend")
        st.line_chart(hist_df.set_index("timestamp")["signal"])

        st.subheader("📈 Data Usage Trend")
        st.line_chart(hist_df.set_index("timestamp")["data_usage"])

    st.subheader("📋 All Devices")
    st.dataframe(df, use_container_width=True)

else:
    st.warning("No devices connected")

