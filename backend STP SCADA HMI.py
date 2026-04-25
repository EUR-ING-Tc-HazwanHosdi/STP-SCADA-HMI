import streamlit as st
import numpy as np
import pandas as pd
import os
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# =========================================================
# CONFIG
# =========================================================
st.set_page_config("STP DIGITAL TWIN V9", layout="wide")

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

for p in PLANTS.values():
    init_file(p)

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
# DIGITAL TWIN SIMULATION (process behavior model)
# =========================================================
def digital_twin(do, nh3, srt, svi):

    nh3 = nh3 + np.random.normal(0, 0.5)
    do = do + np.random.normal(0, 0.2)

    return do, nh3, srt, svi

# =========================================================
# LSTM MODEL (simple forecasting)
# =========================================================

from sklearn.ensemble import RandomForestRegressor

def simple_forecast(df):

    if len(df) < 10:
        return None

    df = df.copy()
    df["t"] = range(len(df))

    X = df[["t"]]
    y = df["NH3"]

    model = RandomForestRegressor(n_estimators=50)
    model.fit(X, y)

    future = [[len(df) + 5]]
    return model.predict(future)[0]

# =========================================================
# UI - MULTI PLANT
# =========================================================
st.title("🏭 Industrial Digital Twin V9")

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

    st.success("Twin step executed")

# =========================================================
# LOAD DATA
# =========================================================
df = pd.read_csv(file)

# =========================================================
# HEALTH ENGINE
# =========================================================
health = 100

if do < 1:
    health -= 40
if nh3 > 10:
    health -= 20
if svi > 150:
    health -= 20
if srt < 5:
    health -= 20

# =========================================================
# KPI DASHBOARD
# =========================================================
c1, c2, c3, c4 = st.columns(4)

c1.metric("DO", round(do,2))
c2.metric("NH3", round(nh3,2))
c3.metric("SRT", round(srt,2))
c4.metric("Health", health)

st.progress(max(health,0))

# =========================================================
# FAULT ENGINE
# =========================================================
st.subheader("🚨 Fault Detection")

faults = []

if nh3 > 10 and srt < 10:
    faults.append("Nitrification Limitation")

if do > 5 and nh3 > 10:
    faults.append("Process Imbalance (High DO but high NH3)")

if svi > 150:
    faults.append("Bulking Risk")

for f in faults:
    st.error(f)

if not faults:
    st.success("Stable Operation")

# =========================================================
# LSTM PREDICTION
# =========================================================
st.subheader("🧠 LSTM NH3 Forecast")

if len(df) > 20:

    data = df[["DO","NH3","SRT","SVI"]].values

    model, scaler = train_lstm(data)

    last_seq = scaler.transform(data[-5:]).reshape(1,5,4)

    pred = model.predict(last_seq)[0][0]

    st.write("Predicted NH3:", float(pred))

    if pred > 15:
        st.error("⚠️ Future NH3 spike predicted")

else:
    st.info("Need more data for LSTM training")

# =========================================================
# DIGITAL TWIN TREND
# =========================================================
st.subheader("📈 Plant Trend")

if len(df) > 0:
    st.line_chart(df.set_index("time")[["DO","NH3"]])

# =========================================================
# MULTI PLANT OVERVIEW
# =========================================================
st.subheader("🌍 Fleet Overview")

summary = []

for name, f in PLANTS.items():
    d = pd.read_csv(f)
    if len(d) > 0:
        summary.append({
            "Plant": name,
            "Last NH3": d["NH3"].iloc[-1],
            "Last DO": d["DO"].iloc[-1]
        })

st.dataframe(pd.DataFrame(summary))