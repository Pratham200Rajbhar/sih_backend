# SafeHorizon API Configuration

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# CSV file paths
CSV_FILES = {
    "tourists": str(DATA_DIR / "tourists.csv"),
    "locations": str(DATA_DIR / "locations.csv"), 
    "alerts": str(DATA_DIR / "alerts.csv"),
    "geofences": str(DATA_DIR / "geofences.csv")
}

# Model file paths
MODEL_FILE = str(MODELS_DIR / "anomaly_model.pkl")
SCALER_FILE = str(MODELS_DIR / "scaler.pkl")

# API Configuration
API_CONFIG = {
    "title": "SafeHorizon API",
    "version": "1.0.0",
    "host": "0.0.0.0",
    "port": 8000,
    "reload": True
}

# CORS Configuration
CORS_CONFIG = {
    "allow_origins": ["*"],  # Configure for production
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"]
}

# ML Configuration
ML_CONFIG = {
    "contamination": 0.1,
    "random_state": 42,
    "retrain_interval": 50  # Retrain every N new locations
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": str(LOGS_DIR / "safehorizon.log")
}