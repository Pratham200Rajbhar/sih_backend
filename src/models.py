# SafeHorizon API - Data Models
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import math

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

# Comprehensive Tourist Information Models
class LocationInfo(BaseModel):
    id: str
    lat: float
    lon: float
    timestamp: str
    speed_kmh: float
    in_geofence: int
    label: str

class AlertInfo(BaseModel):
    id: str
    type: str
    lat: float
    lon: float
    status: str
    created_at: str
    related_location_id: Optional[str] = None

class TouristAnalytics(BaseModel):
    total_locations: int
    total_alerts: int
    anomaly_locations: int
    normal_locations: int
    average_speed: float
    max_speed: float
    min_speed: float
    geofence_violations: int
    sos_alerts: int
    ml_alerts: int
    first_location: Optional[str] = None
    last_location: Optional[str] = None
    total_distance_km: float
    risk_score: float

class TouristSafetyStatus(BaseModel):
    current_status: str  # "SAFE", "AT_RISK", "EMERGENCY", "UNKNOWN"
    last_seen: Optional[str] = None
    current_location: Optional[LocationInfo] = None
    active_alerts: int
    days_since_registration: int

class ComprehensiveTouristInfo(BaseModel):
    # Basic Information
    tourist_id: str
    name: str
    phone: str
    trip_start: str
    trip_end: str
    registration_date: str
    
    # Safety Status
    safety_status: TouristSafetyStatus
    
    # Analytics
    analytics: TouristAnalytics
    
    # Recent Data (last 10 records)
    recent_locations: List[LocationInfo]
    recent_alerts: List[AlertInfo]
    
    # All Data (optional, for detailed view)
    all_locations: Optional[List[LocationInfo]] = None
    all_alerts: Optional[List[AlertInfo]] = None

class TouristSummary(BaseModel):
    tourist_id: str
    name: str
    phone: str
    safety_status: str
    total_locations: int
    total_alerts: int
    last_seen: Optional[str] = None
    risk_score: float

class AllTouristsResponse(BaseModel):
    total_tourists: int
    tourists: List[TouristSummary]
    summary_stats: Dict[str, Any]