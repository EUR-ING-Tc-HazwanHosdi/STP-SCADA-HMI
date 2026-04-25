from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

# -------------------------
# In-memory "SCADA database"
# -------------------------
DB = []

# -------------------------
# AI DIAGNOSTIC ENGINE
# -------------------------
def diagnose(do, nh3, srt, svi):

    faults = []
    actions = []
    status = "STABLE"

    # Nitrification issue
    if nh3 > 10:
        if srt < 10:
            faults.append("Nitrification Failure (Low SRT)")
            actions.append("Increase SRT (reduce sludge wasting)")
        if do < 2:
            faults.append("Nitrification Failure (Low DO)")
            actions.append("Increase aeration")

    # Bulking
    if svi > 150:
        faults.append("Sludge Bulking")
        actions.append("Adjust DO and F/M balance")

    # Washout
    if srt < 5:
        faults.append("Biomass Washout Risk")
        actions.append("STOP sludge wasting")

    # Status logic
    if len(faults) >= 2:
        status = "CRITICAL"
    elif len(faults) == 1:
        status = "WARNING"

    if not faults:
        actions.append("Maintain current operation")

    return {
        "status": status,
        "faults": faults,
        "actions": actions
    }

# -------------------------
# INGEST SCADA DATA
# -------------------------
@app.post("/ingest")
def ingest(data: dict):

    record = {
        "time": str(datetime.now()),
        "DO": data["DO"],
        "NH3": data["NH3"],
        "SRT": data["SRT"],
        "SVI": data["SVI"]
    }

    DB.append(record)

    return {"message": "stored"}

# -------------------------
# GET LATEST + AI RESULT
# -------------------------
@app.get("/latest")
def latest():

    if not DB:
        return {"error": "no data"}

    last = DB[-1]

    analysis = diagnose(
        last["DO"],
        last["NH3"],
        last["SRT"],
        last["SVI"]
    )

    return {
        "data": last,
        "analysis": analysis
    }