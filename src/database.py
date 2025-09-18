# SafeHorizon API - CSV Database Operations
import pandas as pd
import numpy as np
import os
from typing import Dict, Any
from config.settings import CSV_FILES

def init_csv_files():
    """Initialize CSV files with headers if they don't exist"""
    headers = {
        "tourists": ["id", "name", "phone", "trip_start", "trip_end"],
        "locations": ["id", "tourist_id", "lat", "lon", "timestamp", "speed_kmh", "in_geofence", "label"],
        "alerts": ["id", "tourist_id", "type", "lat", "lon", "status", "created_at", "related_location_id"],
        "geofences": ["id", "name", "polygon", "severity"]
    }
    
    for file_key, filename in CSV_FILES.items():
        if not os.path.exists(filename):
            df = pd.DataFrame(columns=headers[file_key])
            df.to_csv(filename, index=False)

def read_csv_safe(filename: str) -> pd.DataFrame:
    """Safely read CSV file, return empty DataFrame if file doesn't exist"""
    try:
        if os.path.exists(filename):
            return pd.read_csv(filename)
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return pd.DataFrame()

def append_to_csv(filename: str, data: Dict[str, Any]):
    """Append a row to CSV file"""
    try:
        df = read_csv_safe(filename)
        new_row = pd.DataFrame([data])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(filename, index=False)
        return True
    except Exception as e:
        print(f"Error appending to {filename}: {e}")
        return False

def update_csv_row(filename: str, row_id: str, updates: Dict[str, Any]):
    """Update a specific row in CSV file"""
    try:
        df = read_csv_safe(filename)
        if df.empty:
            return False
        
        mask = df['id'] == row_id
        if not mask.any():
            return False
            
        for col, value in updates.items():
            df.loc[mask, col] = value
        
        df.to_csv(filename, index=False)
        return True
    except Exception as e:
        print(f"Error updating {filename}: {e}")
        return False

def safe_json_convert(df):
    """Convert DataFrame to JSON-safe format by handling NaN, inf, and -inf values"""
    # Replace NaN, inf, -inf with None for JSON compliance
    df_clean = df.replace([np.nan, np.inf, -np.inf], None)
    return df_clean.to_dict('records')