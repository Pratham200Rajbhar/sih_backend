# SafeHorizon API - Backend Integration Guide for Frontend Developers

## 🚀 Quick Start

### Base URL
```
http://localhost:8000
```

### API Documentation
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📡 API Endpoints Reference

### 1. 👤 Tourist Registration
**POST** `/register`

Register a new tourist in the system.

```javascript
// Request
fetch('http://localhost:8000/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: "John Doe",
    phone: "+919876543210",
    emergency_contact: "+919876543211"
  })
})

// Response
{
  "id": "12345678-1234-1234-1234-123456789abc",
  "name": "John Doe",
  "phone": "+919876543210",
  "emergency_contact": "+919876543211",
  "created_at": "2025-09-19T10:30:00Z"
}
```

### 2. 📍 Location Update
**POST** `/location`

Update tourist's current location for tracking.

```javascript
// Request
fetch('http://localhost:8000/location', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    tourist_id: "12345678-1234-1234-1234-123456789abc",
    latitude: 28.6139,
    longitude: 77.2090,
    timestamp: "2025-09-19T10:30:00Z"
  })
})

// Response
{
  "status": "success",
  "message": "Location updated successfully",
  "anomaly_detected": false,
  "in_safe_zone": true
}
```

### 3. 🆘 SOS Alert
**POST** `/alert/sos`

Send emergency SOS alert.

```javascript
// Request
fetch('http://localhost:8000/alert/sos', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    tourist_id: "12345678-1234-1234-1234-123456789abc",
    latitude: 28.6139,
    longitude: 77.2090,
    message: "Help! I'm lost and need assistance."
  })
})

// Response
{
  "alert_id": "alert_001",
  "status": "created",
  "message": "SOS alert created successfully",
  "priority": "high",
  "emergency_contacts_notified": true
}
```

### 4. 📋 Get All Alerts
**GET** `/alerts`

Retrieve all alerts with optional filtering.

```javascript
// Request (with optional query parameters)
fetch('http://localhost:8000/alerts?status=pending&tourist_id=12345678-1234-1234-1234-123456789abc')

// Response
{
  "alerts": [
    {
      "id": "alert_001",
      "tourist_id": "12345678-1234-1234-1234-123456789abc",
      "type": "sos",
      "status": "pending",
      "latitude": 28.6139,
      "longitude": 77.2090,
      "message": "Help! I'm lost and need assistance.",
      "timestamp": "2025-09-19T10:30:00Z",
      "priority": "high"
    }
  ],
  "total_count": 1
}
```

**Query Parameters:**
- `status`: Filter by alert status (`pending`, `resolved`, `investigating`)
- `tourist_id`: Filter alerts for specific tourist
- `alert_type`: Filter by type (`sos`, `geofence`, `anomaly`)

### 5. ✏️ Update Alert Status
**PATCH** `/alerts/{alert_id}`

Update the status of an existing alert.

```javascript
// Request
fetch('http://localhost:8000/alerts/alert_001', {
  method: 'PATCH',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    status: "resolved",
    notes: "Tourist found safe, assistance provided"
  })
})

// Response
{
  "message": "Alert updated successfully",
  "alert": {
    "id": "alert_001",
    "status": "resolved",
    "notes": "Tourist found safe, assistance provided",
    "updated_at": "2025-09-19T11:00:00Z"
  }
}
```

### 6. 🗺️ Safety Heatmap Data
**GET** `/heatmap`

Get location data for generating safety heatmaps.

```javascript
// Request
fetch('http://localhost:8000/heatmap')

// Response
{
  "heatmap_data": [
    {
      "latitude": 28.6139,
      "longitude": 77.2090,
      "safety_score": 0.85,
      "alert_count": 2,
      "visit_count": 15
    }
  ],
  "metadata": {
    "total_locations": 45,
    "date_range": "2025-09-01 to 2025-09-19",
    "last_updated": "2025-09-19T10:30:00Z"
  }
}
```

### 7. 👤 Get Tourist Details
**GET** `/tourist/{tourist_id}`

Retrieve detailed information about a specific tourist.

```javascript
// Request
fetch('http://localhost:8000/tourist/12345678-1234-1234-1234-123456789abc')

// Response
{
  "tourist": {
    "id": "12345678-1234-1234-1234-123456789abc",
    "name": "John Doe",
    "phone": "+919876543210",
    "emergency_contact": "+919876543211",
    "created_at": "2025-09-19T10:30:00Z",
    "last_location": {
      "latitude": 28.6139,
      "longitude": 77.2090,
      "timestamp": "2025-09-19T10:30:00Z"
    },
    "status": "active"
  },
  "recent_alerts": [
    {
      "id": "alert_001",
      "type": "sos",
      "status": "resolved",
      "timestamp": "2025-09-19T09:15:00Z"
    }
  ],
  "location_history_count": 25
}
```

### 8. 🛡️ Manage Geofences
**POST** `/geofences`

Create a new geofenced safe zone.

```javascript
// Request
fetch('http://localhost:8000/geofences', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: "Tourist Area Safe Zone",
    coordinates: [
      [28.6129, 77.2080],
      [28.6149, 77.2080],
      [28.6149, 77.2100],
      [28.6129, 77.2100],
      [28.6129, 77.2080]
    ],
    zone_type: "safe"
  })
})

// Response
{
  "message": "Geofence created successfully",
  "geofence_id": "geo_001",
  "status": "active"
}
```

---

## 🔧 Frontend Integration Examples

### React Hook for Location Tracking

```jsx
import { useState, useEffect } from 'react';

const useLocationTracking = (touristId) => {
  const [location, setLocation] = useState(null);
  const [isTracking, setIsTracking] = useState(false);

  const updateLocation = async (lat, lng) => {
    try {
      const response = await fetch('http://localhost:8000/location', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tourist_id: touristId,
          latitude: lat,
          longitude: lng,
          timestamp: new Date().toISOString()
        })
      });
      
      const data = await response.json();
      setLocation({ lat, lng, ...data });
      
      // Handle anomaly detection
      if (data.anomaly_detected) {
        alert('Unusual location pattern detected!');
      }
      
    } catch (error) {
      console.error('Location update failed:', error);
    }
  };

  useEffect(() => {
    if (isTracking && navigator.geolocation) {
      const watchId = navigator.geolocation.watchPosition(
        (position) => {
          updateLocation(
            position.coords.latitude,
            position.coords.longitude
          );
        },
        (error) => console.error('Geolocation error:', error),
        { enableHighAccuracy: true, maximumAge: 10000 }
      );

      return () => navigator.geolocation.clearWatch(watchId);
    }
  }, [isTracking, touristId]);

  return { location, isTracking, setIsTracking, updateLocation };
};
```

### Emergency SOS Component

```jsx
const SOSButton = ({ touristId }) => {
  const [isEmergency, setIsEmergency] = useState(false);

  const sendSOS = async () => {
    setIsEmergency(true);
    
    navigator.geolocation.getCurrentPosition(async (position) => {
      try {
        const response = await fetch('http://localhost:8000/alert/sos', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tourist_id: touristId,
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            message: "Emergency assistance required!"
          })
        });
        
        const data = await response.json();
        
        if (response.ok) {
          alert('SOS sent! Help is on the way.');
        } else {
          throw new Error(data.detail || 'SOS failed');
        }
        
      } catch (error) {
        alert('Failed to send SOS. Please try again.');
        console.error('SOS Error:', error);
      } finally {
        setIsEmergency(false);
      }
    });
  };

  return (
    <button 
      onClick={sendSOS}
      disabled={isEmergency}
      className="sos-button"
      style={{
        backgroundColor: '#ff4444',
        color: 'white',
        padding: '15px 30px',
        fontSize: '18px',
        border: 'none',
        borderRadius: '50px',
        cursor: isEmergency ? 'not-allowed' : 'pointer'
      }}
    >
      {isEmergency ? 'Sending SOS...' : '🆘 EMERGENCY'}
    </button>
  );
};
```

### Real-time Alerts Dashboard

```jsx
const AlertsDashboard = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchAlerts = async () => {
    try {
      const response = await fetch('http://localhost:8000/alerts');
      const data = await response.json();
      setAlerts(data.alerts);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateAlertStatus = async (alertId, newStatus) => {
    try {
      const response = await fetch(`http://localhost:8000/alerts/${alertId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: newStatus,
          notes: `Status updated to ${newStatus}`
        })
      });
      
      if (response.ok) {
        fetchAlerts(); // Refresh alerts
      }
    } catch (error) {
      console.error('Failed to update alert:', error);
    }
  };

  useEffect(() => {
    fetchAlerts();
    
    // Poll for new alerts every 30 seconds
    const interval = setInterval(fetchAlerts, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div>Loading alerts...</div>;

  return (
    <div className="alerts-dashboard">
      <h2>Safety Alerts ({alerts.length})</h2>
      {alerts.map(alert => (
        <div key={alert.id} className={`alert alert-${alert.priority}`}>
          <h3>{alert.type.toUpperCase()} Alert</h3>
          <p><strong>Tourist:</strong> {alert.tourist_id}</p>
          <p><strong>Location:</strong> {alert.latitude}, {alert.longitude}</p>
          <p><strong>Message:</strong> {alert.message}</p>
          <p><strong>Status:</strong> {alert.status}</p>
          <p><strong>Time:</strong> {new Date(alert.timestamp).toLocaleString()}</p>
          
          <div className="alert-actions">
            <button onClick={() => updateAlertStatus(alert.id, 'investigating')}>
              Start Investigation
            </button>
            <button onClick={() => updateAlertStatus(alert.id, 'resolved')}>
              Mark Resolved
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};
```

---

## 🗺️ Integrating with Map Libraries

### Leaflet.js Integration

```javascript
// Initialize map with heatmap
const initializeMap = async () => {
  const map = L.map('map').setView([28.6139, 77.2090], 13);
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
  
  // Fetch and display heatmap data
  const response = await fetch('http://localhost:8000/heatmap');
  const data = await response.json();
  
  // Add markers for each location
  data.heatmap_data.forEach(location => {
    const color = location.safety_score > 0.7 ? 'green' : 
                  location.safety_score > 0.4 ? 'orange' : 'red';
    
    L.circleMarker([location.latitude, location.longitude], {
      color: color,
      radius: Math.min(location.visit_count / 2, 20)
    }).bindPopup(`
      Safety Score: ${location.safety_score}<br>
      Alerts: ${location.alert_count}<br>
      Visits: ${location.visit_count}
    `).addTo(map);
  });
};
```

---

## 🚨 Error Handling

### Common HTTP Status Codes

- **200 OK**: Success
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

### Error Response Format

```javascript
{
  "detail": "Error description",
  "type": "validation_error|not_found|server_error",
  "code": "SPECIFIC_ERROR_CODE"
}
```

### Error Handling Example

```javascript
const apiCall = async (url, options) => {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API call failed');
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    
    // Handle different error types
    if (error.message.includes('validation')) {
      alert('Please check your input data');
    } else if (error.message.includes('not found')) {
      alert('Requested resource not found');
    } else {
      alert('Something went wrong. Please try again.');
    }
    
    throw error;
  }
};
```

---

## 🔒 Security Considerations

### CORS Configuration
The API is configured with CORS enabled for development. In production:

```javascript
// The API accepts requests from these origins
const allowedOrigins = [
  'http://localhost:3000',  // React dev server
  'http://localhost:5173',  // Vite dev server
  'https://your-production-domain.com'
];
```

### Rate Limiting
- SOS alerts: No rate limiting (emergency priority)
- Location updates: Max 1 per second per tourist
- Other endpoints: Max 100 requests per minute

---

## 🧪 Testing

### Test the API with curl

```bash
# Register a tourist
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","phone":"+919876543210","emergency_contact":"+919876543211"}'

# Update location
curl -X POST "http://localhost:8000/location" \
  -H "Content-Type: application/json" \
  -d '{"tourist_id":"your-tourist-id","latitude":28.6139,"longitude":77.2090,"timestamp":"2025-09-19T10:30:00Z"}'

# Send SOS
curl -X POST "http://localhost:8000/alert/sos" \
  -H "Content-Type: application/json" \
  -d '{"tourist_id":"your-tourist-id","latitude":28.6139,"longitude":77.2090,"message":"Test emergency"}'
```

---

## 📞 Support

For backend API issues:
- Check the interactive docs: http://localhost:8000/docs
- Review server logs in the `logs/` directory
- Ensure the backend server is running: `uvicorn main:app --reload`

Need help? The API includes comprehensive error messages and logging to help debug integration issues.

---

## 🚀 Getting Started Checklist

1. ✅ Ensure backend server is running on `http://localhost:8000`
2. ✅ Test API endpoints using the interactive docs
3. ✅ Register a test tourist to get a valid `tourist_id`
4. ✅ Implement location tracking in your frontend
5. ✅ Add SOS emergency functionality
6. ✅ Create alerts dashboard for monitoring
7. ✅ Integrate safety heatmap visualization
8. ✅ Implement proper error handling
9. ✅ Test all integration points thoroughly

Happy coding! 🎉