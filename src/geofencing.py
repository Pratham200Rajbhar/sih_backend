# SafeHorizon API - Geofencing Operations
import json
from typing import List, Optional, Dict, Any
from shapely.geometry import Point, Polygon
from src.database import read_csv_safe
from config.settings import CSV_FILES

def point_in_polygon(lat: float, lon: float, polygon_coords: List[List[float]]) -> bool:
    """Check if a point is inside a polygon"""
    try:
        point = Point(lon, lat)  # Note: Shapely uses (x, y) = (lon, lat)
        
        # Validate polygon coordinates
        if len(polygon_coords) < 3:
            print("Error: Polygon must have at least 3 coordinates")
            return False
            
        # Convert polygon coordinates: assume input is [[lat, lon], ...], convert to [(lon, lat), ...]
        polygon_points = []
        for coord in polygon_coords:
            if len(coord) >= 2:
                polygon_points.append((coord[1], coord[0]))  # Convert to (lon, lat)
            else:
                print(f"Error: Invalid coordinate format: {coord}")
                return False
                
        polygon = Polygon(polygon_points)
        return polygon.is_valid and polygon.contains(point)
        
    except (IndexError, TypeError, ValueError) as e:
        print(f"Error in point_in_polygon: {e}")
        return False

def check_geofences(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Check if location is in any restricted geofence"""
    geofences_df = read_csv_safe(CSV_FILES["geofences"])
    
    for _, geofence in geofences_df.iterrows():
        try:
            polygon_data = json.loads(geofence['polygon'])
            if point_in_polygon(lat, lon, polygon_data):
                return {
                    "id": geofence['id'],
                    "name": geofence['name'],
                    "severity": geofence['severity']
                }
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error processing geofence {geofence.get('id', 'unknown')}: {e}")
    
    return None