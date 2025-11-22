"""
Configuration file for Project EcoFlow
Contains database credentials, thresholds, and constants
"""

# ============================================================================
# DATABASE CONFIGURATION (SSH Tunnel)
# ============================================================================
# The SSH tunnel must be active before connecting to the database
# Run: ssh -N -p 2213 -L 15432:localhost:6543 hackathon2025@sensorbox.zapto.org

DB_CONFIG = {
    'host': 'localhost',
    'port': 15432,
    'database': 'sensor_data',
    'user': 'sensorbox_readonly',
    'password': 'Il81,Ry4#QL=Dxz61C'
}

# ============================================================================
# SSH TUNNEL CONFIGURATION
# ============================================================================
SSH_CONFIG = {
    'host': 'sensorbox.zapto.org',
    'port': 2213,
    'username': 'hackathon2025',
    'password': 'Il81,Ry4#QL=Dxz61C'  # Same as DB password
}

# ============================================================================
# AIR QUALITY THRESHOLDS (WHO Guidelines)
# ============================================================================
# PM10: World Health Organization 24-hour mean guideline
WHO_PM10_LIMIT = 45.0  # µg/m³
WHO_PM25_LIMIT = 15.0  # µg/m³

# Custom threshold for emergency rerouting
EMERGENCY_PM10_THRESHOLD = 50.0  # µg/m³
EMERGENCY_PM25_THRESHOLD = 25.0  # µg/m³

# ============================================================================
# TRAFFIC CONFIGURATION
# ============================================================================
# Default traffic capacity (cars per hour)
DEFAULT_CAPACITY_THRESHOLD = 120

# Traffic light timings (seconds)
STANDARD_GREEN_DURATION = 30
EXTENDED_GREEN_DURATION = 60

# ============================================================================
# DEVICE INFORMATION
# ============================================================================
# German device with 1 year of reliable traffic data
# This will be populated after querying the database
GERMAN_DEVICE_IMEI = None  # To be determined from database query

# Heilbronn approximate coordinates (for map visualization)
HEILBRONN_COORDS = {
    'latitude': 49.142,
    'longitude': 9.210
}

# ============================================================================
# DATA EXTRACTION SETTINGS
# ============================================================================
# Number of months to extract for training (full year for better accuracy)
TRAINING_DATA_MONTHS = 12

# ============================================================================
# MODEL SETTINGS
# ============================================================================
MODEL_PATH = 'trained_model.pkl'
MODEL_TR1_PATH = 'trained_model_tr1.pkl'  # Direction 1 model
MODEL_TR2_PATH = 'trained_model_tr2.pkl'  # Direction 2 model
DATA_CACHE_PATH = 'data_cache/'
