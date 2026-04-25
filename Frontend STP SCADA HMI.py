import streamlit as st
import requests

st.set_page_config("STP SCADA V8", layout="wide")

API = "http://127.0.0.1:8000/latest"
INGEST = "http://127.0.0.1:8000/ingest"

st.title("🏭 STP AI SCADA V8")

# -------------------------
# INPUT PANEL (SIMULATION / MANUAL)
# -------------------------
st.sidebar.title("⚙️ Input Control")

do = st.sidebar.slider("DO", 0.0, 10.0, 2.0)
nh3 = st.sidebar.slider("NH3", 0.0, 30.0, 5.0)
srt = st.sidebar.slider("SRT", 0.0, 20.0, 8.0)
svi = st.sidebar.slider("SVI", 50.0, 250.0, 120.0)

if st.sidebar.button("Send to SCADA"):

    requests.post(INGEST, json={
        "DO": do,
        "NH3": nh3,
        "SRT": srt,
        "SVI": svi
    })

    st.success("Data sent to SCADA")

# -------------------------
# FETCH DATA
# -------------------------
res = requests.get(API).json()

if "error" not in res:

    data = res["data"]
    analysis = res["analysis"]

    # -------------------------
    # KPI DASHBOARD
    # -------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("DO", data["DO"])
    col2.metric("NH3", data["NH3"])
    col3.metric("SRT", data["SRT"])
    col4.metric("SVI", data["SVI"])

    # -------------------------
    # STATUS
    # -------------------------
    st.subheader("🚨 System Status")

    if analysis["status"] == "CRITICAL":
        st.error("CRITICAL SYSTEM")
    elif analysis["status"] == "WARNING":
        st.warning("WARNING STATE")
    else:
        st.success("STABLE OPERATION")

    # -------------------------
    # FAULTS
    # -------------------------
    st.subheader("⚠️ Fault Detection")

    if analysis["faults"]:
        for f in analysis["faults"]:
            st.error(f)
    else:
        st.success("No faults detected")

    # -------------------------
    # ACTIONS
    # -------------------------
    st.subheader("⚙️ Recommended Actions")

    for a in analysis["actions"]:
        st.write("👉", a)

else:
    st.warning("No data available yet")