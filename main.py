import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

# Import custom modules
from src.models import (
    TouristRegistration, LocationData, AlertCreate, AlertUpdate, GeofenceData,
    TouristResponse, LocationResponse, AlertResponse, MLStatusResponse, MLAnalysis
)
from src.database import (
    init_csv_files, read_csv_safe, append_to_csv, update_csv_row, safe_json_convert
)
from src.geofencing import check_geofences
from src.ml_engine import load_or_train_model, predict_anomaly, train_anomaly_model, force_retrain, get_ml_status, stop_auto_retrain_monitor
from config.settings import CSV_FILES, API_CONFIG, CORS_CONFIG, ML_CONFIG

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_csv_files()
    load_or_train_model()
    print("✅ SafeHorizon API started successfully with auto-retraining enabled")
    yield
    # Shutdown
    stop_auto_retrain_monitor()
    print("⏹️ SafeHorizon API shutting down")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title=API_CONFIG["title"], 
    version=API_CONFIG["version"], 
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_CONFIG["allow_origins"],
    allow_credentials=CORS_CONFIG["allow_credentials"],
    allow_methods=CORS_CONFIG["allow_methods"],
    allow_headers=CORS_CONFIG["allow_headers"],
)

# API Endpoints

@app.post("/register", response_model=TouristResponse)
async def register_tourist(tourist: TouristRegistration):
    """Register a new tourist"""
    tourist_id = str(uuid.uuid4())
    
    tourist_data = {
        "id": tourist_id,
        "name": tourist.name,
        "phone": tourist.phone,
        "trip_start": tourist.trip_start,
        "trip_end": tourist.trip_end
    }
    
    if append_to_csv(CSV_FILES["tourists"], tourist_data):
        return TouristResponse(tourist_id=tourist_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register tourist"
        )

@app.post("/location", response_model=LocationResponse)
async def submit_location(location: LocationData):
    """Submit location data with geofence and anomaly checking"""
    location_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    # Check geofences
    geofence_alert = check_geofences(location.lat, location.lon)
    in_geofence = 1 if geofence_alert else 0
    
    # Check for anomaly with enhanced prediction
    ml_result = predict_anomaly(
        location.speed_kmh or 0.0, 
        in_geofence, 
        location.lat, 
        location.lon
    )
    
    # Save location data
    location_data = {
        "id": location_id,
        "tourist_id": location.tourist_id,
        "lat": location.lat,
        "lon": location.lon,
        "timestamp": timestamp,
        "speed_kmh": location.speed_kmh or 0.0,
        "in_geofence": in_geofence,
        "label": "anomaly" if ml_result["is_anomaly"] else "normal"
    }
    
    append_to_csv(CSV_FILES["locations"], location_data)
    
    alert_created = False
    
    # Create geofence alert if needed
    if geofence_alert:
        alert_data = {
            "id": str(uuid.uuid4()),
            "tourist_id": location.tourist_id,
            "type": "GeoFence",
            "lat": location.lat,
            "lon": location.lon,
            "status": "OPEN",
            "created_at": timestamp,
            "related_location_id": location_id
        }
        append_to_csv(CSV_FILES["alerts"], alert_data)
        alert_created = True
    
    # Create ML anomaly alert if needed (only for high-confidence anomalies)
    if ml_result["is_anomaly"] and ml_result["confidence"] > 0.3:
        alert_data = {
            "id": str(uuid.uuid4()),
            "tourist_id": location.tourist_id,
            "type": "ML",
            "lat": location.lat,
            "lon": location.lon,
            "status": "OPEN",
            "created_at": timestamp,
            "related_location_id": location_id
        }
        append_to_csv(CSV_FILES["alerts"], alert_data)
        alert_created = True
    
    return LocationResponse(
        status="OK", 
        alert_created=alert_created,
        ml_analysis=MLAnalysis(
            anomaly_detected=bool(ml_result["is_anomaly"]),
            confidence=float(ml_result["confidence"]),
            score=float(ml_result["score"])
        )
    )

@app.post("/alert/sos", response_model=AlertResponse)
async def create_sos_alert(alert: AlertCreate):
    """Create an SOS alert"""
    alert_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    alert_data = {
        "id": alert_id,
        "tourist_id": alert.tourist_id,
        "type": "SOS",
        "lat": alert.lat,
        "lon": alert.lon,
        "status": "OPEN",
        "created_at": timestamp,
        "related_location_id": ""
    }
    
    if append_to_csv(CSV_FILES["alerts"], alert_data):
        return AlertResponse(alert_id=alert_id, status="OPEN")
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create SOS alert"
        )

@app.get("/alerts")
async def get_alerts():
    """Get all alerts"""
    alerts_df = read_csv_safe(CSV_FILES["alerts"])
    return safe_json_convert(alerts_df)

@app.patch("/alerts/{alert_id}")
async def update_alert(alert_id: str, alert_update: AlertUpdate):
    """Update alert status"""
    if update_csv_row(CSV_FILES["alerts"], alert_id, {"status": alert_update.status}):
        return {"message": "Alert updated successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

@app.get("/heatmap")
async def get_heatmap():
    """Get heatmap data with safe and danger zones"""
    locations_df = read_csv_safe(CSV_FILES["locations"])
    alerts_df = read_csv_safe(CSV_FILES["alerts"])
    
    # Get alert locations (danger zones)
    danger_locations = []
    for _, alert in alerts_df.iterrows():
        danger_locations.append({
            "lat": alert["lat"],
            "lon": alert["lon"],
            "type": alert["type"],
            "tourist_id": alert["tourist_id"]
        })
    
    # Get safe locations (exclude alert locations)
    alert_location_ids = set(alerts_df["related_location_id"].dropna())
    safe_locations = []
    
    for _, location in locations_df.iterrows():
        if location["id"] not in alert_location_ids:
            safe_locations.append({
                "lat": location["lat"],
                "lon": location["lon"],
                "tourist_id": location["tourist_id"]
            })
    
    return {
        "safe": safe_locations,
        "danger": danger_locations
    }

@app.get("/tourist/{tourist_id}")
async def get_tourist_details(tourist_id: str):
    """Get tourist details and their alerts"""
    import pandas as pd
    
    tourists_df = read_csv_safe(CSV_FILES["tourists"])
    alerts_df = read_csv_safe(CSV_FILES["alerts"])
    
    # Find tourist
    tourist = tourists_df[tourists_df['id'] == tourist_id]
    if tourist.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tourist not found"
        )
    
    # Get tourist's alerts and convert safely
    tourist_alerts = alerts_df[alerts_df['tourist_id'] == tourist_id]
    
    # Convert tourist data safely
    tourist_dict = tourist.iloc[0].to_dict()
    # Replace NaN values in tourist dict
    tourist_dict = {k: (None if pd.isna(v) else v) for k, v in tourist_dict.items()}
    
    return {
        "tourist": tourist_dict,
        "alerts": safe_json_convert(tourist_alerts)
    }

@app.post("/geofences")
async def create_geofence(geofence: GeofenceData):
    """Create a new geofence (utility endpoint)"""
    import json
    
    geofence_id = str(uuid.uuid4())
    
    geofence_data = {
        "id": geofence_id,
        "name": geofence.name,
        "polygon": json.dumps(geofence.polygon),
        "severity": geofence.severity
    }
    
    if append_to_csv(CSV_FILES["geofences"], geofence_data):
        return {"geofence_id": geofence_id, "message": "Geofence created successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create geofence"
        )

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "SafeHorizon API is running", "version": API_CONFIG["version"]}

# ML Management Endpoints

@app.post("/ml/retrain")
async def manual_retrain():
    """Manually trigger ML model retraining"""
    try:
        success = force_retrain()
        if success:
            return {
                "status": "success",
                "message": "ML model retrained successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrain ML model"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during retraining: {str(e)}"
        )

@app.get("/ml/status", response_model=MLStatusResponse)
async def ml_status():
    """Get current ML model status and statistics"""
    try:
        status_data = get_ml_status()
        return MLStatusResponse(**status_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting ML status: {str(e)}"
        )

@app.post("/ml/predict")
async def test_ml_prediction(
    speed_kmh: float = 50.0,
    in_geofence: int = 0,
    lat: Optional[float] = None,
    lon: Optional[float] = None
):
    """Test ML prediction with custom parameters"""
    try:
        result = predict_anomaly(speed_kmh, in_geofence, lat, lon)
        
        # Ensure all values are JSON serializable
        return {
            "prediction": {
                "is_anomaly": bool(result["is_anomaly"]),
                "confidence": float(result["confidence"]),
                "score": float(result["score"])
            },
            "parameters": {
                "speed_kmh": float(speed_kmh),
                "in_geofence": bool(in_geofence),
                "lat": float(lat) if lat is not None else None,
                "lon": float(lon) if lon is not None else None
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in ML prediction: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=API_CONFIG["host"], 
        port=API_CONFIG["port"],
        reload=API_CONFIG["reload"]
    )
