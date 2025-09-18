# SafeHorizon API - Enhanced Machine Learning Operations with Auto-Retraining
import pandas as pd
import pickle
import os
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from src.database import read_csv_safe
from config.settings import CSV_FILES, MODEL_FILE, SCALER_FILE, ML_CONFIG

# Global variables for ML model
anomaly_model = None
scaler = None
last_training_time = None
last_data_hash = None
retrain_lock = threading.Lock()
auto_retrain_enabled = True
monitor_thread = None

def calculate_data_hash():
    """Calculate hash of all relevant data files for change detection"""
    try:
        hash_string = ""
        for file_type, file_path in CSV_FILES.items():
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                hash_string += f"{file_path}:{stat.st_mtime}:{stat.st_size};"
        return hash(hash_string)
    except Exception as e:
        print(f"Error calculating data hash: {e}")
        return 0

def extract_enhanced_features():
    """Extract enhanced features from all available data"""
    try:
        locations_df = read_csv_safe(CSV_FILES["locations"])
        alerts_df = read_csv_safe(CSV_FILES["alerts"])
        
        if len(locations_df) < 5:
            return None
        
        # Basic features
        features = locations_df[['speed_kmh', 'in_geofence']].fillna(0)
        
        # Enhanced features if we have enough data
        if len(locations_df) > 10:
            # Add time-based features
            locations_df['timestamp'] = pd.to_datetime(locations_df['timestamp'], errors='coerce')
            locations_df['hour'] = locations_df['timestamp'].dt.hour.fillna(12)
            
            # Add location-based risk score
            if len(alerts_df) > 0:
                location_risk = []
                for _, row in locations_df.iterrows():
                    # Count alerts near this location
                    nearby_alerts = alerts_df[
                        (abs(alerts_df['lat'] - row['lat']) < 0.01) & 
                        (abs(alerts_df['lon'] - row['lon']) < 0.01)
                    ]
                    risk_score = len(nearby_alerts) / max(len(alerts_df), 1)
                    location_risk.append(risk_score)
                
                features['location_risk'] = location_risk
            else:
                features['location_risk'] = 0
            
            # Add speed anomaly score
            speed_mean = locations_df['speed_kmh'].mean()
            speed_std = locations_df['speed_kmh'].std()
            if speed_std > 0:
                features['speed_anomaly'] = abs(features['speed_kmh'] - speed_mean) / speed_std
            else:
                features['speed_anomaly'] = 0
            
            # Add hour of day
            features['hour'] = locations_df['hour'].fillna(12)
        
        return features.fillna(0)
        
    except Exception as e:
        print(f"Error extracting enhanced features: {e}")
        return None

def train_anomaly_model():
    """Train IsolationForest model using enhanced features"""
    global anomaly_model, scaler, last_training_time
    
    try:
        print("🤖 Starting ML model training...")
        
        # Extract features
        features_df = extract_enhanced_features()
        
        if features_df is None or len(features_df) < 5:
            print("Insufficient data for ML training. Using basic model.")
            # Create basic model with minimal features
            scaler = StandardScaler()
            anomaly_model = IsolationForest(
                contamination=ML_CONFIG["contamination"], 
                random_state=ML_CONFIG["random_state"]
            )
            # Fit with dummy data
            dummy_data = pd.DataFrame([[30, 0], [40, 1], [50, 0]], columns=['speed_kmh', 'in_geofence'])
            scaler.fit(dummy_data)
            anomaly_model.fit(dummy_data)
        else:
            # Scale features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features_df)
            
            # Train enhanced model
            contamination = min(0.2, max(0.05, ML_CONFIG["contamination"]))  # Dynamic contamination
            anomaly_model = IsolationForest(
                contamination=contamination,
                random_state=ML_CONFIG["random_state"],
                n_estimators=100,
                max_samples='auto'
            )
            anomaly_model.fit(features_scaled)
            
            print(f"✅ ML model trained with {len(features_df)} samples using {len(features_df.columns)} features")
            print(f"📊 Features: {list(features_df.columns)}")
        
        # Save model and scaler
        os.makedirs(os.path.dirname(MODEL_FILE), exist_ok=True)
        with open(MODEL_FILE, 'wb') as f:
            pickle.dump(anomaly_model, f)
        with open(SCALER_FILE, 'wb') as f:
            pickle.dump(scaler, f)
        
        last_training_time = datetime.now()
        print(f"🎯 Model saved successfully at {last_training_time}")
            
    except Exception as e:
        print(f"❌ Error training ML model: {e}")

def should_retrain():
    """Check if model should be retrained based on data changes"""
    global last_data_hash, last_training_time
    
    try:
        # Check if enough time has passed (minimum 30 seconds between retrains)
        if last_training_time:
            time_since_training = datetime.now() - last_training_time
            if time_since_training < timedelta(seconds=30):
                return False
        
        # Check if data has changed
        current_hash = calculate_data_hash()
        if last_data_hash is None or current_hash != last_data_hash:
            last_data_hash = current_hash
            return True
        
        return False
        
    except Exception as e:
        print(f"Error checking retrain condition: {e}")
        return False

def auto_retrain_monitor():
    """Background thread to monitor data changes and auto-retrain"""
    global auto_retrain_enabled
    
    print("🔄 Auto-retrain monitor started")
    
    while auto_retrain_enabled:
        try:
            if should_retrain():
                with retrain_lock:
                    print("📊 Data changes detected - starting auto-retrain...")
                    train_anomaly_model()
            
            time.sleep(10)  # Check every 10 seconds
            
        except Exception as e:
            print(f"Error in auto-retrain monitor: {e}")
            time.sleep(30)  # Wait longer on error

def start_auto_retrain_monitor():
    """Start the auto-retrain monitoring thread"""
    global monitor_thread, auto_retrain_enabled
    
    if monitor_thread is None or not monitor_thread.is_alive():
        auto_retrain_enabled = True
        monitor_thread = threading.Thread(target=auto_retrain_monitor, daemon=True)
        monitor_thread.start()
        print("✅ Auto-retrain monitor started")

def stop_auto_retrain_monitor():
    """Stop the auto-retrain monitoring"""
    global auto_retrain_enabled
    auto_retrain_enabled = False
    print("⏹️ Auto-retrain monitor stopped")

def load_or_train_model():
    """Load existing model or train new one, then start auto-monitoring"""
    global anomaly_model, scaler
    
    try:
        if os.path.exists(MODEL_FILE) and os.path.exists(SCALER_FILE):
            with open(MODEL_FILE, 'rb') as f:
                anomaly_model = pickle.load(f)
            with open(SCALER_FILE, 'rb') as f:
                scaler = pickle.load(f)
            print("📂 Loaded existing ML model")
        else:
            print("🆕 No existing model found, training new one...")
            train_anomaly_model()
        
        # Start auto-retrain monitoring
        start_auto_retrain_monitor()
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        train_anomaly_model()
        start_auto_retrain_monitor()

def force_retrain():
    """Force immediate retraining (useful for API endpoints)"""
    global last_data_hash
    
    try:
        with retrain_lock:
            print("🔄 Force retraining ML model...")
            last_data_hash = None  # Reset hash to force retrain
            train_anomaly_model()
            return True
    except Exception as e:
        print(f"❌ Error in force retrain: {e}")
        return False

def predict_anomaly(speed_kmh: float, in_geofence: int, lat: float = None, lon: float = None) -> dict:
    """Enhanced anomaly prediction with confidence scoring"""
    global anomaly_model, scaler
    
    try:
        if anomaly_model is None or scaler is None:
            return {"is_anomaly": False, "confidence": 0.0, "score": 0.0}
        
        # Prepare features based on what the model was trained with
        try:
            # Try to get the feature names from the scaler
            n_features = scaler.n_features_in_
        except:
            n_features = 2  # Default to basic features
        
        if n_features == 2:
            # Basic model
            features_df = pd.DataFrame([[speed_kmh, in_geofence]], columns=['speed_kmh', 'in_geofence'])
        else:
            # Enhanced model - calculate additional features
            alerts_df = read_csv_safe(CSV_FILES["alerts"])
            
            # Calculate location risk if coordinates provided
            location_risk = 0
            if lat is not None and lon is not None and len(alerts_df) > 0:
                nearby_alerts = alerts_df[
                    (abs(alerts_df['lat'] - lat) < 0.01) & 
                    (abs(alerts_df['lon'] - lon) < 0.01)
                ]
                location_risk = len(nearby_alerts) / max(len(alerts_df), 1)
            
            # Calculate speed anomaly
            locations_df = read_csv_safe(CSV_FILES["locations"])
            speed_anomaly = 0
            if len(locations_df) > 0:
                speed_mean = locations_df['speed_kmh'].mean()
                speed_std = locations_df['speed_kmh'].std()
                if speed_std > 0:
                    speed_anomaly = abs(speed_kmh - speed_mean) / speed_std
            
            # Current hour
            current_hour = datetime.now().hour
            
            # Create feature vector
            features_df = pd.DataFrame([[
                speed_kmh, in_geofence, location_risk, speed_anomaly, current_hour
            ]], columns=['speed_kmh', 'in_geofence', 'location_risk', 'speed_anomaly', 'hour'])
            
            # Pad or trim features to match model expectations
            if len(features_df.columns) < n_features:
                for i in range(len(features_df.columns), n_features):
                    features_df[f'feature_{i}'] = 0
            elif len(features_df.columns) > n_features:
                features_df = features_df.iloc[:, :n_features]
        
        # Make prediction
        features_scaled = scaler.transform(features_df)
        prediction = anomaly_model.predict(features_scaled)
        decision_score = anomaly_model.decision_function(features_scaled)[0]
        
        is_anomaly = prediction[0] == -1
        confidence = abs(decision_score)
        
        return {
            "is_anomaly": bool(is_anomaly),  # Convert numpy.bool_ to Python bool
            "confidence": float(confidence),
            "score": float(decision_score)
        }
        
    except Exception as e:
        print(f"❌ Error in anomaly prediction: {e}")
        return {"is_anomaly": False, "confidence": 0.0, "score": 0.0}

def get_ml_status():
    """Get current ML model status"""
    global last_training_time, auto_retrain_enabled, monitor_thread
    
    return {
        "model_loaded": anomaly_model is not None,
        "scaler_loaded": scaler is not None,
        "last_training": last_training_time.isoformat() if last_training_time else None,
        "auto_retrain_enabled": auto_retrain_enabled,
        "monitor_running": monitor_thread is not None and monitor_thread.is_alive(),
        "model_file_exists": os.path.exists(MODEL_FILE),
        "scaler_file_exists": os.path.exists(SCALER_FILE)
    }