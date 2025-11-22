# 🚦 Project EcoFlow

**Smart Traffic Light & Routing System for Climate-Conscious Cities**

![Hackathon](https://img.shields.io/badge/Hackathon-Future%20City%202025-blue)
![Challenge](https://img.shields.io/badge/Challenge-Smart%20Climate%20City-green)
![Status](https://img.shields.io/badge/Status-Active-success)

---

## 🎯 The Problem

Traditional traffic management systems optimize for **speed only**, ignoring environmental impact. This creates a vicious cycle:
- Traffic jams increase vehicle emissions
- Static traffic lights can't adapt to changing conditions
- Air quality deteriorates in busy intersections
- **Public health suffers**

## 💡 Our Solution

**EcoFlow** is an intelligent traffic control system that optimizes for **BOTH** traffic flow AND air quality using:

1. **🧠 AI Prediction**: Prophet ML model forecasts traffic patterns based on historical data
2. **⚙️ Smart Logic**: Adaptive intersection control with climate override
3. **📊 Real-time Data**: Integration with SensorBox IoT network (26 devices across Europe)

### Key Innovation: Climate Override

Unlike traditional systems, EcoFlow can **prioritize public health over traffic flow** by:
- Extending green lights during rush hour to reduce stop-and-go emissions
- **Rerouting traffic when air pollution reaches hazardous levels**
- Balancing mobility with environmental protection

---

## 🏗️ Architecture

```
┌─────────────────────┐
│  SensorBox Network  │  26 devices (IT + DE)
│  Traffic + Air Data │  1 year historical data
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Data Extraction    │  PostgreSQL/TimescaleDB
│  data_extraction.py │  SSH Tunnel Connection
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  AI Model (Prophet) │  Traffic Forecasting
│  model.py           │  24-hour predictions
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Logic Engine       │  Smart Decisions
│  logic.py           │  Congestion + Climate
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Dashboard          │  Visual Demo
│  app.py (Streamlit) │  3 Demo Modes
└─────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ (Python 3.9+ recommended)
- SSH access to SensorBox database (for data extraction)
- Active SSH tunnel (see setup below)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Smart Climate City"
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python3 -m venv venv

   # On macOS/Linux:
   source venv/bin/activate

   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   **Note**: This will install all required packages including:
   - Streamlit (dashboard)
   - Prophet (ML model)
   - Pandas, NumPy (data processing)
   - psycopg2-binary (database connection)
   - Plotly (visualization)

3. **Set up SSH tunnel** (keep this running in a separate terminal)
   ```bash
   ssh -N -p 2213 -L 15432:localhost:6543 hackathon2025@sensorbox.zapto.org
   # Password: Il81,Ry4#QL=Dxz61C
   ```

### Usage

#### Step 1: Extract Data (Optional - only if training model)

```bash
python data_extraction.py
```

This will:
- Connect to the SensorBox database
- Identify the German device with historical traffic data
- Extract 12 months of traffic data
- Extract air quality statistics from Italian devices
- Save data to `data_cache/` directory

**Note**: If you don't have database access, you can skip this step if the `data_cache/` directory already contains the CSV files.

#### Step 2: Train Model (Optional - only if you want to use real predictions)

```bash
python model.py
```

This will:
- Load the extracted traffic data from `data_cache/german_traffic_12m.csv`
- Train Prophet models on historical patterns (total, TR1, TR2)
- Save the trained models to `trained_model.pkl`, `trained_model_tr1.pkl`, `trained_model_tr2.pkl`
- Generate sample 24-hour forecast

**Note**: If you don't have the training data, you can skip this step if the `trained_model*.pkl` files already exist in the repository.

#### Step 3: Run Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

**Note**: Make sure your virtual environment is activated before running this command!

---

## 📦 Repository Setup

### What's Included vs. What's Excluded

**✅ Included in Repository:**
- All Python source files (`.py`)
- Configuration files (`config.py`, `requirements.txt`)
- Documentation (`.md` files)
- Data cache directory structure (CSV files may be large - consider Git LFS)
- Trained model files (`.pkl` - optional, can be regenerated)

**❌ Excluded from Repository (via `.gitignore`):**
- `venv/` - Virtual environment (recreated with `python -m venv venv`)
- `__pycache__/` - Python cache files
- `.DS_Store`, `Thumbs.db` - OS files
- IDE files (`.vscode/`, `.idea/`)

### For Repository Maintainers

If you're setting up the repository for the first time:

1. **Create `.gitignore`** (already included):
   ```bash
   # The .gitignore file excludes venv/ and other unnecessary files
   ```

2. **Decide what to commit:**
   - **Option A**: Commit trained models (`.pkl` files) - Others can use immediately
   - **Option B**: Don't commit models - Others must train them (takes ~5-10 minutes)
   - **Option C**: Use Git LFS for large files (models, CSV data)

3. **If models are NOT committed**, users need to:
   - Run `python data_extraction.py` (if they have DB access)
   - OR use pre-extracted CSV files if available
   - Run `python model.py` to train models

---

## 🎮 Demo Modes

The dashboard includes three pre-configured demo scenarios:

### ✅ Standard Mode
- **Traffic**: 50 cars/hr (low)
- **Air Quality**: 20 µg/m³ PM10 (good)
- **Result**: Normal operation with standard 30s green lights

### ⚡ Rush Hour Mode
- **Traffic**: 150 cars/hr (high)
- **Air Quality**: 25 µg/m³ PM10 (acceptable)
- **Result**: Extended 60s green lights to maximize flow

### ⛔ Emergency Mode
- **Traffic**: 80 cars/hr (moderate)
- **Air Quality**: 65 µg/m³ PM10 (hazardous)
- **Result**: **Climate Override** - traffic rerouted to protect public health

You can also use **Manual Control** to experiment with custom parameters!

---

## 📁 Project Structure

```
Smart Climate City/
├── app.py                  # Streamlit dashboard (main application)
├── data_extraction.py      # Database connection & data retrieval
├── model.py                # Prophet ML model for traffic prediction
├── logic.py                # Smart intersection decision engine
├── config.py               # Configuration and constants
├── requirements.txt        # Python dependencies
├── README.md               # This file
│
├── data_cache/             # Cached data files (created on first run)
│   ├── german_traffic_6m.csv
│   ├── air_quality_stats.csv
│   └── device_locations.csv
│
└── trained_model.pkl       # Saved Prophet model (created after training)
```

---

## 🔬 Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **ML/AI**: Facebook Prophet (time series forecasting)
- **Database**: PostgreSQL/TimescaleDB (via SSH tunnel)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly, Streamlit native charts
- **Data Source**: SensorBox IoT Network (iLCS - ED40)

---

## 📊 Data Sources

### German Device (1 device)
- **Duration**: 1 year of historical data
- **Sensors**: Traffic (TR1, TR2), Air Quality, Noise
- **Quality**: ✅ High reliability
- **Use Case**: Model training, trend analysis

### Italian Devices (~25 devices)
- **Duration**: 1 month of recent data
- **Sensors**: Air Quality (reliable), Traffic (commissioning phase), Noise
- **Quality**: ✅ Air quality data reliable, ⚠️ Traffic data experimental
- **Use Case**: Air quality thresholds, spatial analysis

---

## ⚙️ Configuration

Edit `config.py` to customize:

- **Database credentials** (default provided)
- **Air quality thresholds** (WHO guidelines)
- **Traffic capacity limits** (default: 120 cars/hr)
- **Green light durations** (standard: 30s, extended: 60s)
- **Training data period** (default: 6 months)

---

## 🧪 Testing Components Individually

Test each module independently:

```bash
# Test database connection
python -c "from data_extraction import test_connection; test_connection()"

# Test logic engine
python logic.py

# Test model (requires data)
python model.py
```

---

## 🏆 Hackathon Success Criteria

### ✅ The Story
- **Problem**: Traffic jams cause pollution. Static lights are inefficient.
- **Solution**: EcoFlow uses AI + real-time sensors to optimize for flow AND health.

### ✅ The Tech
- **Data Usage**: Trained on reliable German dataset (1 year)
- **Innovation**: Climate Override feature - first traffic system that protects public health
- **Scalability**: Designed to deploy across entire Italian network

### ✅ The Demo
- Standard Mode: Normal operation ✅
- Rush Hour Mode: Extended green lights ✅
- Emergency Mode: Climate override with rerouting ✅

---

## 🎨 Dashboard Features

- **Premium Design**: Modern gradient UI with glassmorphism effects
- **Real-time Metrics**: Live traffic and air quality indicators
- **Interactive Controls**: Manual sliders or preset demo modes
- **Health Impact**: WHO-aligned air quality assessment
- **Network Map**: Geographic visualization of sensor network
- **Status Indicators**: Color-coded traffic light states

---

## 🚨 Troubleshooting

### SSH Tunnel Issues

**Problem**: Database connection fails

**Solution**:
```bash
# Check if tunnel is running
lsof -i :15432

# Restart tunnel if needed
ssh -N -p 2213 -L 15432:localhost:6543 hackathon2025@sensorbox.zapto.org
```

### Dashboard Issues

**Problem**: Streamlit app won't start

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Clear Streamlit cache
streamlit cache clear

# Run with verbose logging
streamlit run app.py --logger.level=debug
```

### Demo Mode (No Database)

If you can't access the database, the app will still work in demo mode:
- Dashboard uses simulated predictions
- All three demo modes function normally
- No real data required

---

## 📈 Future Enhancements

- **Real-time MQTT Integration**: Live sensor data streaming
- **Multi-intersection Coordination**: Network-wide optimization
- **Mobile App**: Citizen air quality alerts
- **Historical Playback**: Replay actual traffic events
- **Weather Integration**: Factor in meteorological data

---

## 👥 Credits

**Project**: EcoFlow
**Event**: Future City Hackathon 2025 (Heilbronn)
**Challenge**: Smart Climate City - Traffic & Air Quality
**Data Provider**: iLCS - ED40 (SensorBox IoT Network)

### Technologies
- Data: SensorBox Network (26 devices in IT/DE)
- ML: Facebook Prophet
- Dashboard: Streamlit
- Database: PostgreSQL/TimescaleDB

---

## 📄 License

This project was created for the Future City Hackathon 2025. Data usage is governed by the hackathon terms and conditions.

---

## 🌟 Key Takeaway

> **EcoFlow proves that smart cities can balance mobility AND sustainability. By using AI to predict traffic and real-time sensors to monitor air quality, we can create transportation systems that protect both traffic flow and public health.**

**Let's build cleaner, smarter cities together! 🌍🚦**
