# SafeHorizon API - Data Models
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TouristRegistration(BaseModel):
    name: str
    phone: str
    trip_start: str  # ISO date string
    trip_end: str    # ISO date string

class LocationData(BaseModel):
    tourist_id: str
    lat: float
    lon: float
    speed_kmh: Optional[float] = 0.0

class AlertCreate(BaseModel):
    tourist_id: str
    lat: float
    lon: float

class AlertUpdate(BaseModel):
    status: str = Field(..., pattern="^(OPEN|RESOLVED|CLOSED)$")

class GeofenceData(BaseModel):
    name: str
    polygon: List[List[float]]  # Array of [lat, lon] coordinates
    severity: str = Field(..., pattern="^(LOW|MEDIUM|HIGH)$")

# Response Models
class TouristResponse(BaseModel):
    tourist_id: str

class MLAnalysis(BaseModel):
    anomaly_detected: bool
    confidence: float
    score: float

class LocationResponse(BaseModel):
    status: str
    alert_created: bool
    ml_analysis: Optional[MLAnalysis] = None

class AlertResponse(BaseModel):
    alert_id: str
    status: str

class MLStatusResponse(BaseModel):
    model_loaded: bool
    auto_retrain_enabled: bool
    monitor_running: bool
    last_training: Optional[str] = None