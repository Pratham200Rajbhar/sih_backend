# SafeHorizon API Test Script
# Run this after starting the server to test all endpoints

import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("🚀 Testing SafeHorizon API...")
    
    # Test 1: Register a tourist
    print("\n1. Testing POST /register")
    tourist_data = {
        "name": "John Doe",
        "phone": "+91-9876543210",
        "trip_start": "2025-09-18T10:00:00",
        "trip_end": "2025-09-25T18:00:00"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=tourist_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        tourist_id = response.json()["tourist_id"]
        print(f"Tourist ID: {tourist_id}")
    else:
        print("Failed to register tourist")
        return
    
    # Test 2: Create a geofence
    print("\n2. Testing POST /geofences")
    geofence_data = {
        "name": "Restricted Area",
        "polygon": [
            [28.6139, 77.2090],  # Delhi coordinates
            [28.6149, 77.2090],
            [28.6149, 77.2100],
            [28.6139, 77.2100]
        ],
        "severity": "HIGH"
    }
    
    response = requests.post(f"{BASE_URL}/geofences", json=geofence_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Geofence created: {response.json()}")
    
    # Test 3: Submit location (safe)
    print("\n3. Testing POST /location (safe location)")
    location_data = {
        "tourist_id": tourist_id,
        "lat": 28.6000,  # Outside geofence
        "lon": 77.2000,
        "speed_kmh": 30.0
    }
    
    response = requests.post(f"{BASE_URL}/location", json=location_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 4: Submit location (dangerous - inside geofence)
    print("\n4. Testing POST /location (inside geofence)")
    location_data = {
        "tourist_id": tourist_id,
        "lat": 28.6145,  # Inside geofence
        "lon": 77.2095,
        "speed_kmh": 25.0
    }
    
    response = requests.post(f"{BASE_URL}/location", json=location_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 5: Create SOS alert
    print("\n5. Testing POST /alert/sos")
    sos_data = {
        "tourist_id": tourist_id,
        "lat": 28.6145,
        "lon": 77.2095
    }
    
    response = requests.post(f"{BASE_URL}/alert/sos", json=sos_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        alert_id = response.json()["alert_id"]
        print(f"SOS Alert ID: {alert_id}")
    
    # Test 6: Get all alerts
    print("\n6. Testing GET /alerts")
    response = requests.get(f"{BASE_URL}/alerts")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        alerts = response.json()
        print(f"Total alerts: {len(alerts)}")
        for alert in alerts:
            print(f"  - {alert['type']} alert for tourist {alert['tourist_id'][:8]}...")
    
    # Test 7: Get heatmap data
    print("\n7. Testing GET /heatmap")
    response = requests.get(f"{BASE_URL}/heatmap")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        heatmap = response.json()
        print(f"Safe locations: {len(heatmap['safe'])}")
        print(f"Danger locations: {len(heatmap['danger'])}")
    
    # Test 8: Get tourist details
    print("\n8. Testing GET /tourist/{id}")
    response = requests.get(f"{BASE_URL}/tourist/{tourist_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        tourist_info = response.json()
        print(f"Tourist: {tourist_info['tourist']['name']}")
        print(f"Alerts for this tourist: {len(tourist_info['alerts'])}")
    
    print("\n✅ API testing completed!")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error during testing: {e}")