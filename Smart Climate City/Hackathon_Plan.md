🚦 Project EcoFlow: Master Execution Plan

Event: Future City Hackathon 2025 (Heilbronn)

Challenge: Smart Climate City (Traffic & Air Quality)

Goal: Build a "Smart Traffic Light & Routing" prototype that optimizes for Flow AND Climate.

🏗️ High-Level Architecture

We are building a 3-part system:

The Brain (AI Model): Predicts traffic volume using reliable historical data from the German sensor.

The Logic Engine: Decides if lights should stay GREEN longer or if cars should be REROUTED based on pollution.

The Dashboard (Streamlit): A visual demo showing the "City View" with simulated intersections responding to our logic.

🗓️ Phase 1: Data Extraction & Setup (Hours 1-4)

Goal: Secure the data before doing anything complex.

1.1 Establish Connection

Follow the ACCESS_GUIDE.md to open the SSH Tunnel.

# Terminal 1 (Keep Open)
ssh -N -p 2213 -L 15432:localhost:6543 hackathon2025@sensorbox.zapto.org
# Password: [See Guide]


1.2 Extract Reliable Traffic Data (The "German" Dataset)

We need to find the ONE reliable device in Germany to train our model.

Strategy: Start with 6 months of data to test code quickly. Once the model works, re-run with 1 year for the final demo.

SQL Query (Python/Pandas):

import psycopg2
import pandas as pd

def get_german_traffic_data(months=6):
    conn = psycopg2.connect(
        host="localhost", port="15432", database="sensor_data",
        user="sensorbox_readonly", password="Il81,Ry4#QL=Dxz61C"
    )

    # 1. Get the German Device IMEI (assuming latitude is Heilbronn area ~49.1)
    # Or just query specific IMEIs if known.
    # For now, we pull data for the device with the most history.

    query = f"""
    SELECT timestamp, tr1, tr2, imei
    FROM trafficsensordata
    WHERE timestamp > NOW() - INTERVAL '{months} months'
    -- Add IMEI filter here once identified
    ORDER BY timestamp ASC
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df


1.3 Extract Air Quality Reference

We need to know what "Bad Air" looks like to set our thresholds.

Query: Get p10 (PM10) and p02 (PM2.5) from Italian devices to calculate average "High Pollution" levels.

🧠 Phase 2: The Prediction Model (Hours 4-10)

Goal: A function that tells us "Is it Rush Hour?"

2.1 Train the Model

We use Prophet because it handles weekends/holidays automatically.

model.py:

from prophet import Prophet
import pandas as pd

def train_traffic_model(df):
    # Prepare data for Prophet
    df['y'] = df['tr1'] + df['tr2'] # Total Volume
    df['ds'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)

    m = Prophet(daily_seasonality=True, weekly_seasonality=True)
    m.fit(df)
    return m

def get_prediction(model, future_hours=24):
    future = model.make_future_dataframe(periods=future_hours, freq='H')
    forecast = model.predict(future)
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]


⚙️ Phase 3: The Logic Engine (Hours 10-14)

Goal: The "Smart" part. Defining the rules.

logic.py:

class SmartIntersection:
    def __init__(self, name, capacity_threshold=100):
        self.name = name
        self.capacity = capacity_threshold
        self.state = "NORMAL"
        self.green_light_duration = 30 # Standard 30s

    def decide(self, predicted_traffic, current_aqi):
        """
        Inputs:
        - predicted_traffic (int): Cars per hour
        - current_aqi (float): PM10 level
        """

        # Rule 1: Congestion Management
        if predicted_traffic > self.capacity:
            self.green_light_duration = 60 # Double Green Time
            traffic_status = "HEAVY"
        else:
            self.green_light_duration = 30
            traffic_status = "NORMAL"

        # Rule 2: Climate Override (The Hackathon Winner Feature)
        # If pollution is toxic, we deliberately throttle traffic or reroute
        if current_aqi > 50.0: # WHO Threshold approx
            self.state = "⛔ REROUTING (Toxic Air)"
            # In a real system, this would turn red or change digital signs
        elif traffic_status == "HEAVY":
            self.state = f"🟢 MAX FLOW (Green: {self.green_light_duration}s)"
        else:
            self.state = f"🟢 STANDARD (Green: {self.green_light_duration}s)"

        return self.state


💻 Phase 4: The Dashboard & Demo (Hours 14-20)

Goal: Visualization. This is what the judges see.

Tool: Streamlit
Why: It creates a web app instantly from Python scripts.

app.py:

import streamlit as st
import pandas as pd
from logic import SmartIntersection

st.set_page_config(layout="wide")
st.title("🚦 EcoFlow: Intelligent Traffic Control")

# --- SIDEBAR: SIMULATION CONTROLS ---
st.sidebar.header("👮 Control Room (Simulation)")
sim_traffic = st.sidebar.slider("Traffic Volume (Cars/hr)", 0, 200, 50)
sim_aqi = st.sidebar.slider("Air Quality (PM10)", 0, 100, 20)

# --- MAIN DASHBOARD ---
col1, col2 = st.columns(2)

# Visualization 1: The Smart Intersection
with col1:
    st.subheader("📍 Intersection: Heilbronn Center")

    # Instantiate Logic
    intersection = SmartIntersection("Center", capacity_threshold=120)
    status = intersection.decide(sim_traffic, sim_aqi)

    # Display Status
    if "REROUTE" in status:
        st.error(status)
        st.markdown("### ⚠️ ACTION: Digital Signs set to 'Detour'")
    elif "MAX FLOW" in status:
        st.warning(status)
        st.markdown("### ⚡ ACTION: Green Light Cycle Extended")
    else:
        st.success(status)
        st.markdown("### ✅ ACTION: Standard Operation")

# Visualization 2: Live Data Metrics
with col2:
    st.subheader("📊 Live Sensor Metrics")
    st.metric("Predicted Traffic", f"{sim_traffic} cars/h", delta_color="inverse")
    st.metric("Live Air Quality", f"{sim_aqi} µg/m³",
              delta=f"{50-sim_aqi} to limit", delta_color="normal")

# Visualization 3: Map (Track 1)
# Use the coordinates from device_mapping table here
st.map(pd.DataFrame({'lat': [49.142], 'lon': [9.210]}))


🏆 Hackathon Checklist: The "Win" Criteria

1. The Story

[ ] Problem: "Traffic jams cause pollution. Static traffic lights are dumb."

[ ] Solution: "EcoFlow uses AI to predict jams and real-time air sensors to prevent smog buildup."

2. The Tech

[ ] Data Usage: Explicitly mention: "We trained on the reliable German dataset for accuracy, but our system is designed to deploy across the Italian network."

[ ] Innovation: Highlight the Climate Override. Most traffic systems only care about speed. Ours cares about Health.

3. The Demo

[ ] Show the Standard Mode (Low traffic, Good air).

[ ] Show the Rush Hour Mode (High traffic -> Extended Green light).

[ ] Show the Emergency Mode (Toxic Air -> Rerouting).

⚠️ Emergency Tips

SSH Tunnel Died? Check if your laptop went to sleep. Restart the tunnel command.

Model Training too slow? Cut the data down to 3 months. Accuracy doesn't matter as much as a working pipeline for the demo.

Streamlit keeps crashing? Remove heavy plots. Stick to st.metric and simple st.line_chart.
