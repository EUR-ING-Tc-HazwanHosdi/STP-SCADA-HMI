import streamlit as st
import numpy as np
import pandas as pd
import os
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor

# =========================================================
# CONFIGURATION 
# =========================================================
st.set_page_config("STP DIGITAL TWIN V9 FIXED", layout="wide")

PLANTS = {
    "Plant A - Industrial": "plant_a.csv",
    "Plant B - Residential": "plant_b.csv",
    "Plant C - Mixed Load": "plant_c.csv"
}

# =========================================================
# INIT FILES
# =========================================================
def init_file(file):
    if not os.path.exists(file):
        df = pd.DataFrame(columns=["time","DO","NH3","SRT","SVI"])
        df.to_csv(file, index=False)

for f in PLANTS.values():
    init_file(f)

# =========================================================
# SAVE DATA
# =========================================================
def save_data(file, do, nh3, srt, svi):
    df = pd.read_csv(file)

    new = {
        "time": str(datetime.now()),
        "DO": do,
        "NH3": nh3,
        "SRT": srt,
        "SVI": svi
    }

    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    df.to_csv(file, index=False)

# =========================================================
# DIGITAL TWIN SIMULATION
# =========================================================
def digital_twin(do, nh3, srt, svi):

    do = do + np.random.normal(0, 0.2)
    nh3 = nh3 + np.random.normal(0, 0.5)

    return do, nh3, srt, svi

# =========================================================
# SIMPLE AI FORECAST (NO TENSORFLOW)
# =========================================================
def forecast_nh3(df):

    if len(df) < 10:
        return None

    df = df.copy()
    df["t"] = range(len(df))

    X = df[["t"]]
    y = df["NH3"]

    model = RandomForestRegressor(n_estimators=80, random_state=42)
    model.fit(X, y)

    future = [[len(df) + 5]]
    return model.predict(future)[0]

# =========================================================
# AI FAULT ENGINE
# =========================================================
def diagnose(do, nh3, srt, svi):

    faults = []

    if nh3 > 10 and srt < 10:
        faults.append("⚠️ Nitrification Limitation (Low SRT)")

    if do > 5 and nh3 > 10:
        faults.append("⚠️ Process Imbalance (High DO + High NH3)")

    if svi > 150:
        faults.append("⚠️ Bulking Risk")

    if srt < 5:
        faults.append("🚨 Biomass Washout Risk")

    return faults

# =========================================================
# HEALTH ENGINE
# =========================================================
def health_score(do, nh3, srt, svi):

    score = 100

    if do < 1:
        score -= 40
    if nh3 > 10:
        score -= 20
    if svi > 150:
        score -= 20
    if srt < 5:
        score -= 20

    return max(score, 0)

# =========================================================
# UI
# =========================================================
st.title("🏭 Industrial Digital Twin V9 (FIXED VERSION)")

plant_name = st.sidebar.selectbox("Select Plant", list(PLANTS.keys()))
file = PLANTS[plant_name]

# =========================================================
# INPUTS
# =========================================================
st.sidebar.subheader("Operator Inputs")

do = st.sidebar.slider("DO", 0.0, 10.0, 2.0)
nh3 = st.sidebar.slider("NH3", 0.0, 30.0, 5.0)
srt = st.sidebar.slider("SRT", 0.0, 20.0, 8.0)
svi = st.sidebar.slider("SVI", 50.0, 250.0, 120.0)

if st.sidebar.button("Run Digital Twin Step"):

    do, nh3, srt, svi = digital_twin(do, nh3, srt, svi)

    save_data(file, do, nh3, srt, svi)

    st.success("Digital twin step executed")

# =========================================================
# LOAD DATA
# =========================================================
df = pd.read_csv(file)

# =========================================================
# ENGINEERING CALCS
# =========================================================
health = health_score(do, nh3, srt, svi)
faults = diagnose(do, nh3, srt, svi)

# =========================================================
# KPI DASHBOARD
# =========================================================
c1, c2, c3, c4 = st.columns(4)

c1.metric("DO", round(do,2))
c2.metric("NH3", round(nh3,2))
c3.metric("SRT", round(srt,2))
c4.metric("Health", health)

st.progress(health)

# =========================================================
# FAULT DISPLAY
# =========================================================
st.subheader("🚨 Fault Detection Engine")

if faults:
    for f in faults:
        st.error(f)
else:
    st.success("Stable Operation")

# =========================================================
# PREDICTION ENGINE
# =========================================================
st.subheader("🧠 NH3 Forecast (AI)")

pred = forecast_nh3(df)

if pred:
    st.write("Predicted NH3 (next cycle):", round(pred, 2))

    if pred > 15:
        st.error("⚠️ Future NH3 spike predicted")
else:
    st.info("Not enough data for prediction (need ≥10 records)")

# =========================================================
# TREND
# =========================================================
st.subheader("📈 Plant Trend")

if len(df) > 0:
    st.line_chart(df.set_index("time")[["DO","NH3"]])

# =========================================================
# MULTI-PLANT OVERVIEW
# =========================================================
st.subheader("🌍 Fleet Overview")

summary = []

for name, f in PLANTS.items():
    d = pd.read_csv(f)

    if len(d) > 0:
        summary.append({
            "Plant": name,
            "Last DO": d["DO"].iloc[-1],
            "Last NH3": d["NH3"].iloc[-1],
            "Health": health_score(
                d["DO"].iloc[-1],
                d["NH3"].iloc[-1],
                d["SRT"].iloc[-1],
                d["SVI"].iloc[-1],
            )
        })

st.dataframe(pd.DataFrame(summary))