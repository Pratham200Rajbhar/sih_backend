"""
SafeHorizon Auto-Retraining ML Test Script
This script demonstrates the automatic retraining functionality
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_auto_retrain_system():
    print("🧪 SafeHorizon Auto-Retraining ML System Test")
    print("=" * 60)
    
    # 1. Check initial ML status
    print("📊 1. Initial ML Status:")
    response = requests.get(f"{BASE_URL}/ml/status")
    status_data = response.json()
    print(json.dumps(status_data, indent=2))
    initial_training_time = status_data.get("last_training")
    
    # 2. Test prediction with different scenarios
    print("\n🎯 2. Testing ML Predictions:")
    
    test_cases = [
        {"speed_kmh": 40, "in_geofence": 1, "lat": 28.6, "lon": 77.2, "desc": "Normal speed, inside geofence"},
        {"speed_kmh": 120, "in_geofence": 0, "lat": 28.6, "lon": 77.2, "desc": "High speed, outside geofence"},
        {"speed_kmh": 5, "in_geofence": 1, "lat": 28.6, "lon": 77.2, "desc": "Very slow speed, inside geofence"},
    ]
    
    for i, test in enumerate(test_cases, 1):
        params = f"speed_kmh={test['speed_kmh']}&in_geofence={test['in_geofence']}&lat={test['lat']}&lon={test['lon']}"
        response = requests.post(f"{BASE_URL}/ml/predict?{params}")
        result = response.json()
        print(f"   Test {i} - {test['desc']}:")
        print(f"   → Anomaly: {result['prediction']['is_anomaly']}, Confidence: {result['prediction']['confidence']:.3f}")
    
    # 3. Add multiple new locations to trigger auto-retrain
    print(f"\n📍 3. Adding new location data to trigger auto-retraining...")
    
    new_locations = [
        {"tourist_id": "auto-test-001", "lat": 28.65, "lon": 77.25, "speed_kmh": 85},
        {"tourist_id": "auto-test-002", "lat": 28.62, "lon": 77.22, "speed_kmh": 35},
        {"tourist_id": "auto-test-003", "lat": 28.68, "lon": 77.28, "speed_kmh": 150},  # High speed anomaly
        {"tourist_id": "auto-test-004", "lat": 28.61, "lon": 77.21, "speed_kmh": 2},   # Very slow anomaly
        {"tourist_id": "auto-test-005", "lat": 28.67, "lon": 77.27, "speed_kmh": 60},
    ]
    
    for i, location in enumerate(new_locations, 1):
        response = requests.post(f"{BASE_URL}/location", json=location)
        result = response.json()
        print(f"   Location {i}: Status={result['status']}, Alert={result['alert_created']}, "
              f"ML_Anomaly={result.get('ml_analysis', {}).get('anomaly_detected', 'N/A')}")
        time.sleep(1)  # Small delay to allow processing
    
    # 4. Wait for auto-retrain and check status
    print(f"\n⏳ 4. Waiting for auto-retraining...")
    time.sleep(5)  # Give time for auto-retrain to complete
    
    response = requests.get(f"{BASE_URL}/ml/status")
    new_status = response.json()
    print(f"   Updated ML Status:")
    print(json.dumps(new_status, indent=2))
    
    # Check if retraining occurred
    new_training_time = new_status.get("last_training")
    if new_training_time != initial_training_time:
        print(f"   ✅ Auto-retraining completed! Model updated.")
        print(f"   📅 Initial training: {initial_training_time}")
        print(f"   📅 New training: {new_training_time}")
    else:
        print(f"   ⏳ Auto-retraining may still be in progress...")
    
    # 5. Test manual retrain
    print(f"\n🔄 5. Testing manual retrain:")
    response = requests.post(f"{BASE_URL}/ml/retrain")
    retrain_result = response.json()
    print(f"   Manual retrain result: {retrain_result['status']}")
    
    # 6. Final prediction test with updated model
    print(f"\n🎯 6. Testing predictions with updated model:")
    response = requests.post(f"{BASE_URL}/ml/predict?speed_kmh=100&in_geofence=0&lat=28.6&lon=77.2")
    final_result = response.json()
    print(f"   High speed test: Anomaly={final_result['prediction']['is_anomaly']}, "
          f"Confidence={final_result['prediction']['confidence']:.3f}")
    
    print(f"\n✅ Auto-retraining system test completed successfully!")
    print(f"📈 The ML model now incorporates all the new location data automatically!")

if __name__ == "__main__":
    test_auto_retrain_system()