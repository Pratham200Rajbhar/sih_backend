# SafeHorizon API - Tourist Analytics Helper Functions
import pandas as pd
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from src.database import read_csv_safe
from config.settings import CSV_FILES

def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates using Haversine formula"""
    if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
        return 0.0
    
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    return c * r

def calculate_total_distance(locations_df: pd.DataFrame) -> float:
    """Calculate total distance traveled by tourist"""
    if len(locations_df) < 2:
        return 0.0
    
    total_distance = 0.0
    locations_df = locations_df.sort_values('timestamp')
    
    for i in range(1, len(locations_df)):
        prev_loc = locations_df.iloc[i-1]
        curr_loc = locations_df.iloc[i]
        
        distance = calculate_distance_km(
            prev_loc['lat'], prev_loc['lon'],
            curr_loc['lat'], curr_loc['lon']
        )
        total_distance += distance
    
    return round(total_distance, 2)

def calculate_risk_score(tourist_id: str, locations_df: pd.DataFrame, alerts_df: pd.DataFrame) -> float:
    """Calculate risk score for tourist based on various factors"""
    if len(locations_df) == 0:
        return 0.5  # Unknown risk
    
    risk_factors = []
    
    # 1. Alert frequency (0-1 scale)
    tourist_alerts = alerts_df[alerts_df['tourist_id'] == tourist_id]
    alert_ratio = len(tourist_alerts) / max(len(locations_df), 1)
    risk_factors.append(min(alert_ratio * 2, 1.0))  # Scale to 0-1
    
    # 2. Anomaly frequency (0-1 scale)
    anomaly_locations = locations_df[locations_df['label'] == 'anomaly']
    anomaly_ratio = len(anomaly_locations) / len(locations_df)
    risk_factors.append(anomaly_ratio)
    
    # 3. Speed risk (0-1 scale)
    avg_speed = locations_df['speed_kmh'].mean()
    if avg_speed > 80:  # High speed risk
        speed_risk = min((avg_speed - 80) / 40, 1.0)  # Scale 80-120 to 0-1
    elif avg_speed < 5:  # Very low speed risk
        speed_risk = min((5 - avg_speed) / 5, 1.0)
    else:
        speed_risk = 0.0
    risk_factors.append(speed_risk)
    
    # 4. Geofence violations (0-1 scale)
    geofence_violations = len(locations_df[locations_df['in_geofence'] == 0])
    violation_ratio = geofence_violations / len(locations_df)
    risk_factors.append(violation_ratio)
    
    # 5. Recent activity (0-1 scale)
    if len(locations_df) > 0:
        latest_timestamp = pd.to_datetime(locations_df['timestamp'].max())
        hours_since_last = (datetime.now() - latest_timestamp).total_seconds() / 3600
        if hours_since_last > 24:  # More than 24 hours
            inactivity_risk = min(hours_since_last / 48, 1.0)  # Scale 24-72 hours to 0-1
        else:
            inactivity_risk = 0.0
        risk_factors.append(inactivity_risk)
    else:
        risk_factors.append(1.0)  # No data is high risk
    
    # Calculate weighted average
    weights = [0.3, 0.25, 0.2, 0.15, 0.1]  # Alerts, anomalies, speed, geofence, activity
    weighted_risk = sum(rf * w for rf, w in zip(risk_factors, weights))
    
    return round(min(max(weighted_risk, 0.0), 1.0), 3)

def determine_safety_status(risk_score: float, active_alerts: int, hours_since_last: float) -> str:
    """Determine overall safety status"""
    if active_alerts > 0:
        # Check for emergency alerts
        alerts_df = read_csv_safe(CSV_FILES["alerts"])
        emergency_alerts = alerts_df[
            (alerts_df['type'] == 'SOS') & 
            (alerts_df['status'] == 'OPEN')
        ]
        if len(emergency_alerts) > 0:
            return "EMERGENCY"
        else:
            return "AT_RISK"
    
    if hours_since_last > 48:  # No contact for 48+ hours
        return "UNKNOWN"
    elif risk_score > 0.7:
        return "AT_RISK"
    elif risk_score > 0.4:
        return "MODERATE_RISK"
    else:
        return "SAFE"

def get_tourist_analytics(tourist_id: str) -> Dict[str, Any]:
    """Calculate comprehensive analytics for a tourist"""
    try:
        # Load data
        locations_df = read_csv_safe(CSV_FILES["locations"])
        alerts_df = read_csv_safe(CSV_FILES["alerts"])
        
        # Filter for specific tourist
        tourist_locations = locations_df[locations_df['tourist_id'] == tourist_id]
        tourist_alerts = alerts_df[alerts_df['tourist_id'] == tourist_id]
        
        if len(tourist_locations) == 0:
            return {
                "total_locations": 0,
                "total_alerts": len(tourist_alerts),
                "anomaly_locations": 0,
                "normal_locations": 0,
                "average_speed": 0.0,
                "max_speed": 0.0,
                "min_speed": 0.0,
                "geofence_violations": 0,
                "sos_alerts": 0,
                "ml_alerts": 0,
                "first_location": None,
                "last_location": None,
                "total_distance_km": 0.0,
                "risk_score": 0.5
            }
        
        # Basic statistics
        total_locations = len(tourist_locations)
        anomaly_locations = len(tourist_locations[tourist_locations['label'] == 'anomaly'])
        normal_locations = total_locations - anomaly_locations
        
        # Speed statistics
        speeds = tourist_locations['speed_kmh'].fillna(0)
        avg_speed = round(speeds.mean(), 2)
        max_speed = round(speeds.max(), 2)
        min_speed = round(speeds.min(), 2)
        
        # Location statistics
        geofence_violations = len(tourist_locations[tourist_locations['in_geofence'] == 0])
        
        # Alert statistics
        sos_alerts = len(tourist_alerts[tourist_alerts['type'] == 'SOS'])
        ml_alerts = len(tourist_alerts[tourist_alerts['type'] == 'ML'])
        
        # Time statistics
        tourist_locations_sorted = tourist_locations.sort_values('timestamp')
        first_location = tourist_locations_sorted['timestamp'].iloc[0] if len(tourist_locations_sorted) > 0 else None
        last_location = tourist_locations_sorted['timestamp'].iloc[-1] if len(tourist_locations_sorted) > 0 else None
        
        # Distance calculation
        total_distance = calculate_total_distance(tourist_locations)
        
        # Risk score
        risk_score = calculate_risk_score(tourist_id, tourist_locations, tourist_alerts)
        
        return {
            "total_locations": total_locations,
            "total_alerts": len(tourist_alerts),
            "anomaly_locations": anomaly_locations,
            "normal_locations": normal_locations,
            "average_speed": avg_speed,
            "max_speed": max_speed,
            "min_speed": min_speed,
            "geofence_violations": geofence_violations,
            "sos_alerts": sos_alerts,
            "ml_alerts": ml_alerts,
            "first_location": first_location,
            "last_location": last_location,
            "total_distance_km": total_distance,
            "risk_score": risk_score
        }
        
    except Exception as e:
        print(f"Error calculating tourist analytics: {e}")
        return {
            "total_locations": 0,
            "total_alerts": 0,
            "anomaly_locations": 0,
            "normal_locations": 0,
            "average_speed": 0.0,
            "max_speed": 0.0,
            "min_speed": 0.0,
            "geofence_violations": 0,
            "sos_alerts": 0,
            "ml_alerts": 0,
            "first_location": None,
            "last_location": None,
            "total_distance_km": 0.0,
            "risk_score": 0.5
        }

def get_safety_status(tourist_id: str) -> Dict[str, Any]:
    """Get current safety status for tourist"""
    try:
        locations_df = read_csv_safe(CSV_FILES["locations"])
        alerts_df = read_csv_safe(CSV_FILES["alerts"])
        tourists_df = read_csv_safe(CSV_FILES["tourists"])
        
        # Get tourist locations and alerts
        tourist_locations = locations_df[locations_df['tourist_id'] == tourist_id]
        tourist_alerts = alerts_df[alerts_df['tourist_id'] == tourist_id]
        tourist_info = tourists_df[tourists_df['id'] == tourist_id]
        
        # Calculate time since last seen
        last_seen = None
        hours_since_last = 999
        current_location = None
        
        if len(tourist_locations) > 0:
            tourist_locations_sorted = tourist_locations.sort_values('timestamp')
            last_location = tourist_locations_sorted.iloc[-1]
            last_seen = last_location['timestamp']
            
            last_timestamp = pd.to_datetime(last_seen)
            hours_since_last = (datetime.now() - last_timestamp).total_seconds() / 3600
            
            current_location = {
                "id": last_location['id'],
                "lat": last_location['lat'],
                "lon": last_location['lon'],
                "timestamp": last_location['timestamp'],
                "speed_kmh": last_location['speed_kmh'],
                "in_geofence": last_location['in_geofence'],
                "label": last_location['label']
            }
        
        # Count active alerts
        active_alerts = len(tourist_alerts[tourist_alerts['status'] == 'OPEN'])
        
        # Calculate days since registration
        days_since_registration = 0
        if len(tourist_info) > 0:
            reg_date = pd.to_datetime(tourist_info.iloc[0]['trip_start'])
            days_since_registration = (datetime.now() - reg_date).days
        
        # Calculate risk score for status determination
        analytics = get_tourist_analytics(tourist_id)
        risk_score = analytics['risk_score']
        
        # Determine status
        status = determine_safety_status(risk_score, active_alerts, hours_since_last)
        
        return {
            "current_status": status,
            "last_seen": last_seen,
            "current_location": current_location,
            "active_alerts": active_alerts,
            "days_since_registration": days_since_registration
        }
        
    except Exception as e:
        print(f"Error getting safety status: {e}")
        return {
            "current_status": "UNKNOWN",
            "last_seen": None,
            "current_location": None,
            "active_alerts": 0,
            "days_since_registration": 0
        }