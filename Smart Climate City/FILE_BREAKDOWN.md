# Project EcoFlow - Complete File Breakdown

This document explains what each file in the project does and how they work together.

---

## 📁 Core Application Files

### 1. **`app.py`** - Main Dashboard Application
**Purpose**: The Streamlit web application that serves as the user interface for the entire system.

**What it does**:
- **UI Components**: Creates the interactive dashboard with custom CSS styling
- **Time Selection**: Allows users to select any date/time (up to 2026) for predictions
- **AI Predictions Display**: Shows real-time traffic predictions from the Prophet model
  - Total traffic predictions
  - Direction-specific predictions (TR1 and TR2)
  - Confidence intervals and ranges
- **Statistics Section**: Displays traffic patterns, rush hour times, and historical data analysis
- **Video Embed**: Shows the future system demonstration video
- **Map Visualization**: Displays sensor locations on an interactive map
- **Smart Intersection Status**: Shows current traffic light decisions based on traffic and air quality
- **Caching**: Uses Streamlit caching for performance optimization

**Key Functions**:
- `load_traffic_model()`: Loads the trained Prophet model from disk
- `get_cached_predictions()`: Gets predictions with caching (refreshes every 15 minutes)
- `get_traffic_statistics()`: Analyzes historical data to show rush hours and patterns

**Dependencies**: `logic.py`, `model.py`, `config.py`

---

### 2. **`model.py`** - Machine Learning Model
**Purpose**: Implements the Prophet time series forecasting model for traffic prediction.

**What it does**:
- **TrafficPredictor Class**: Main class for traffic prediction
  - Trains Prophet models on historical traffic data
  - Creates separate models for:
    - Total traffic (combined TR1 + TR2)
    - Direction 1 (TR1) traffic
    - Direction 2 (TR2) traffic
- **Data Processing**:
  - Aggregates 1-minute data to 15-minute intervals
  - Prepares data in Prophet format (datetime 'ds' and value 'y')
- **Training**:
  - Uses 12 months of historical data
  - Configures Prophet with daily, weekly, and yearly seasonality
  - Saves trained models to `.pkl` files
- **Prediction**:
  - `get_current_prediction()`: Predicts traffic for a specific future time
  - `predict()`: Generates forecasts for multiple hours ahead
  - Handles direction-specific predictions
  - Caps predictions at reasonable maximums

**Key Methods**:
- `train()`: Trains the Prophet models
- `get_current_prediction()`: Gets prediction for a specific time
- `predict()`: Generates multi-hour forecasts
- `save_model()` / `load_model()`: Persistence

**Output Files**:
- `trained_model.pkl`: Total traffic model
- `trained_model_tr1.pkl`: Direction 1 model
- `trained_model_tr2.pkl`: Direction 2 model

---

### 3. **`logic.py`** - Smart Intersection Decision Engine
**Purpose**: Implements the business logic for making traffic control decisions.

**What it does**:
- **SmartIntersection Class**: Core decision-making logic
  - Takes predicted traffic and current air quality as inputs
  - Makes decisions about:
    - Green light duration (standard 30s or extended 60s)
    - Whether to trigger rerouting due to air pollution
  - Three decision modes:
    1. **NORMAL**: Standard operation (traffic < capacity, good air quality)
    2. **MAX FLOW**: Extended green lights (traffic > capacity)
    3. **REROUTING**: Emergency mode (air pollution exceeds safe limits)
- **Health Impact Calculator**:
  - `calculate_health_impact()`: Categorizes air quality based on PM10 levels
  - Uses WHO guidelines (Excellent, Good, Moderate, Unhealthy, Hazardous)
- **TrafficNetwork Class**: Manages multiple intersections (for future expansion)

**Decision Rules**:
1. **Congestion Management**: If traffic > capacity threshold → extend green light
2. **Climate Override**: If PM10 > 50 µg/m³ → trigger rerouting (prioritize health over traffic)

**Dependencies**: `config.py` (for thresholds)

---

### 4. **`data_extraction.py`** - Database Connection & Data Extraction
**Purpose**: Connects to the SensorBox database and extracts training data.

**What it does**:
- **Database Connection**:
  - Connects via SSH tunnel to PostgreSQL/TimescaleDB
  - Tests connection before data extraction
- **Device Identification**:
  - `get_german_device_imei()`: Finds the German device with most traffic data
  - Queries device_mapping table for device information
- **Data Extraction**:
  - `get_german_traffic_data()`: Extracts 12 months of traffic data
    - Gets TR1, TR2, and total traffic
    - Saves to CSV: `data_cache/german_traffic_12m.csv`
  - `get_air_quality_statistics()`: Extracts air quality data from Italian devices
    - Calculates averages and max values for PM10/PM2.5
    - Saves to CSV: `data_cache/air_quality_stats.csv`
  - `get_device_locations()`: Gets GPS coordinates for all devices
    - Saves to CSV: `data_cache/device_locations.csv`

**Database Tables Used**:
- `trafficsensordata`: Traffic sensor readings (TR1, TR2)
- `airqsensordata`: Air quality readings (PM10, PM2.5)
- `device_mapping`: Device metadata (location, GPS, friendly names)

**Output**: CSV files in `data_cache/` directory

---

### 5. **`config.py`** - Configuration & Constants
**Purpose**: Central configuration file for all settings and constants.

**What it contains**:
- **Database Configuration**:
  - Connection credentials for PostgreSQL
  - SSH tunnel settings
- **Air Quality Thresholds**:
  - WHO guidelines (PM10: 45 µg/m³, PM2.5: 15 µg/m³)
  - Emergency thresholds for rerouting
- **Traffic Configuration**:
  - Default capacity threshold (1000 cars/hr)
  - Green light durations (standard: 30s, extended: 60s)
- **Model Settings**:
  - Training data period (12 months)
  - Model file paths
- **Location Data**:
  - Heilbronn coordinates (for map display)

**Why it exists**: Centralizes all configuration so changes don't require editing multiple files.

---

## 📊 Data Files

### 6. **`data_cache/german_traffic_12m.csv`**
**Purpose**: Historical traffic data for model training.

**Contents**:
- 222,402 records of 1-minute traffic measurements
- Columns: `timestamp`, `imei`, `tr1`, `tr2`, `total_traffic`
- Date range: 12 months from May 2025 to November 2025
- Source: German sensor device (Fulda, Germany)

**Usage**: Loaded by `model.py` for training Prophet models

---

### 7. **`data_cache/air_quality_stats.csv`**
**Purpose**: Air quality statistics from Italian sensors.

**Contents**:
- Statistics from 23 Italian sensor locations
- Columns: location, average/max PM10, average/max PM2.5, temperature, humidity
- Used to understand typical pollution levels

**Usage**: Reference data for setting air quality thresholds

---

### 8. **`data_cache/device_locations.csv`**
**Purpose**: GPS coordinates of all sensors.

**Contents**:
- Device IMEI, friendly names, locations, latitude/longitude
- Used for map visualization

**Usage**: Displayed on the map in `app.py`

---

## 🤖 Trained Models

### 9. **`trained_model.pkl`**
**Purpose**: Pickled Prophet model for total traffic prediction.

**Contents**:
- Trained Prophet model
- Device IMEI
- Training date
- Direction model flags

**Usage**: Loaded by `app.py` to make real-time predictions

---

### 10. **`trained_model_tr1.pkl`** & **`trained_model_tr2.pkl`**
**Purpose**: Direction-specific Prophet models.

**Contents**:
- Separate models for TR1 (Direction 1) and TR2 (Direction 2)
- Allows predicting traffic for each direction independently

**Usage**: Loaded when direction-specific predictions are requested

---

## 📄 Documentation Files

### 11. **`README.md`**
**Purpose**: Main project documentation.

**Contents**:
- Project overview
- Architecture diagram
- Quick start guide
- Setup instructions
- Technology stack

---

### 12. **`requirements.txt`**
**Purpose**: Python package dependencies.

**Contents**:
- List of all required Python packages
- Version specifications

**Usage**: `pip install -r requirements.txt` to install dependencies

---

### 13. **`Hackathon_Plan.md`**
**Purpose**: Original project plan and roadmap.

**Contents**:
- Development phases
- Feature specifications
- Implementation notes

---

### 14. **`DATA_ANALYSIS.md`**
**Purpose**: Analysis of extracted sensor data.

**Contents**:
- Traffic statistics
- Air quality patterns
- Data insights

---

### 15. **`MODEL_RESULTS.md`**
**Purpose**: Documentation of model training results.

**Contents**:
- Training statistics
- Prediction examples
- Model performance

---

## 🎬 Media Files

### 16. **`Future_Video.mov`**
**Purpose**: Demonstration video showing future system capabilities.

**Usage**: Embedded in the dashboard to show theoretical future behavior

---

## 🔄 How Files Work Together

### **Data Flow**:
1. **`data_extraction.py`** → Extracts data from database → Saves to CSV
2. **`model.py`** → Reads CSV → Trains Prophet models → Saves `.pkl` files
3. **`app.py`** → Loads `.pkl` models → Makes predictions → Displays on dashboard
4. **`logic.py`** → Takes predictions + air quality → Makes decisions → Returns status
5. **`app.py`** → Displays decisions and status to user

### **Execution Flow**:
```
1. Setup: Install dependencies (requirements.txt)
2. Extract: Run data_extraction.py → Get CSV files
3. Train: Run model.py → Generate .pkl model files
4. Run: Run streamlit run app.py → Launch dashboard
5. Use: Dashboard loads models, makes predictions, shows results
```

### **Configuration Flow**:
- All settings in `config.py`
- Other files import from `config.py`
- Change settings in one place, affects entire system

---

## 🎯 Key Concepts

### **15-Minute Intervals**:
- Raw data: 1-minute measurements
- Model training: Aggregated to 15-minute intervals
- Predictions: Made for 15-minute windows
- Why: Reduces noise, faster training, more stable predictions

### **Direction-Aware Predictions**:
- Three separate models: Total, TR1, TR2
- Allows seeing traffic split between directions
- Helps identify traffic imbalances

### **Caching Strategy**:
- Model loading: Cached with `@st.cache_resource`
- Predictions: Cached for 15 minutes with `@st.cache_data`
- Statistics: Cached for 1 hour (don't change often)

### **Smart Decision Logic**:
- Priority 1: Health (air quality emergency → reroute)
- Priority 2: Traffic flow (high traffic → extend green lights)
- Priority 3: Normal operation

---

## 🚀 Quick Reference

| File | Purpose | When to Run |
|------|---------|-------------|
| `data_extraction.py` | Get data from database | Once, before training |
| `model.py` | Train ML models | After data extraction |
| `app.py` | Launch dashboard | Anytime (via `streamlit run app.py`) |
| `logic.py` | Decision engine | Used by app.py automatically |
| `config.py` | Settings | Edit to change thresholds/constants |

---

This breakdown should help you understand how each component fits into the overall system! 🎉

