# SafeHorizon API 🛡️

A FastAPI-based backend for tourist safety monitoring with geofencing, SOS alerts, and ML-powered anomaly detection.

## Features

- **Tourist Registration**: Register tourists with trip details
- **Real-time Location Tracking**: Track tourist locations with geofence monitoring
- **Geofencing**: Define restricted areas and automatically detect violations
- **SOS Alerts**: Emergency alert system for tourists in distress
- **ML Anomaly Detection**: Machine learning-powered detection of unusual patterns
- **Heatmap Data**: Visualize safe and dangerous zones
- **Alert Management**: Create, view, and manage alerts with status updates

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Pandas**: Data manipulation and CSV file handling
- **Scikit-learn**: Machine learning with IsolationForest for anomaly detection
- **Shapely**: Geospatial operations for point-in-polygon detection
- **Pydantic**: Data validation and settings management
- **UUID**: Unique identifier generation

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Server**:
   ```bash
   python main.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Access API Documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Tourist Management

#### `POST /register`
Register a new tourist.

**Request Body**:
```json
{
  "name": "John Doe",
  "phone": "+91-9876543210",
  "trip_start": "2025-09-18T10:00:00",
  "trip_end": "2025-09-25T18:00:00"
}
```

**Response**:
```json
{
  "tourist_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### `GET /tourist/{id}`
Get tourist details and their alerts.

**Response**:
```json
{
  "tourist": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "John Doe",
    "phone": "+91-9876543210",
    "trip_start": "2025-09-18T10:00:00",
    "trip_end": "2025-09-25T18:00:00"
  },
  "alerts": [...]
}
```

### Location Tracking

#### `POST /location`
Submit location data with automatic geofence and anomaly checking.

**Request Body**:
```json
{
  "tourist_id": "550e8400-e29b-41d4-a716-446655440000",
  "lat": 28.6139,
  "lon": 77.2090,
  "speed_kmh": 30.0
}
```

**Response**:
```json
{
  "status": "OK",
  "alert_created": true
}
```

### Alert Management

#### `POST /alert/sos`
Create an SOS emergency alert.

**Request Body**:
```json
{
  "tourist_id": "550e8400-e29b-41d4-a716-446655440000",
  "lat": 28.6139,
  "lon": 77.2090
}
```

**Response**:
```json
{
  "alert_id": "660f8400-e29b-41d4-a716-446655440111",
  "status": "OPEN"
}
```

#### `GET /alerts`
Retrieve all alerts.

**Response**:
```json
[
  {
    "id": "660f8400-e29b-41d4-a716-446655440111",
    "tourist_id": "550e8400-e29b-41d4-a716-446655440000",
    "type": "SOS",
    "lat": 28.6139,
    "lon": 77.2090,
    "status": "OPEN",
    "created_at": "2025-09-18T14:30:00",
    "related_location_id": ""
  }
]
```

#### `PATCH /alerts/{id}`
Update alert status.

**Request Body**:
```json
{
  "status": "RESOLVED"
}
```

### Data Visualization

#### `GET /heatmap`
Get heatmap data for visualization.

**Response**:
```json
{
  "safe": [
    {
      "lat": 28.6000,
      "lon": 77.2000,
      "tourist_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  ],
  "danger": [
    {
      "lat": 28.6139,
      "lon": 77.2090,
      "type": "SOS",
      "tourist_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  ]
}
```

### Geofence Management

#### `POST /geofences`
Create a new geofence (restricted area).

**Request Body**:
```json
{
  "name": "Restricted Area",
  "polygon": [
    [28.6139, 77.2090],
    [28.6149, 77.2090],
    [28.6149, 77.2100],
    [28.6139, 77.2100]
  ],
  "severity": "HIGH"
}
```

## Data Storage (CSV Files)

### `tourists.csv`
- **id**: Unique tourist identifier (UUID)
- **name**: Tourist's full name
- **phone**: Contact phone number
- **trip_start**: Trip start date/time (ISO format)
- **trip_end**: Trip end date/time (ISO format)

### `locations.csv`
- **id**: Unique location record identifier (UUID)
- **tourist_id**: Reference to tourist
- **lat**: Latitude coordinate
- **lon**: Longitude coordinate
- **timestamp**: Location timestamp (ISO format)
- **speed_kmh**: Speed in kilometers per hour
- **in_geofence**: Binary flag (1 if inside restricted area)
- **label**: ML classification ("normal" or "anomaly")

### `alerts.csv`
- **id**: Unique alert identifier (UUID)
- **tourist_id**: Reference to tourist
- **type**: Alert type ("SOS", "GeoFence", or "ML")
- **lat**: Alert location latitude
- **lon**: Alert location longitude
- **status**: Alert status ("OPEN", "RESOLVED", "CLOSED")
- **created_at**: Alert creation timestamp (ISO format)
- **related_location_id**: Reference to location record (if applicable)

### `geofences.csv`
- **id**: Unique geofence identifier (UUID)
- **name**: Geofence name/description
- **polygon**: JSON array of coordinates defining the restricted area
- **severity**: Risk level ("LOW", "MEDIUM", "HIGH")

## Machine Learning Features

### Anomaly Detection
- **Algorithm**: IsolationForest (unsupervised learning)
- **Features**: Speed and geofence status
- **Training**: Automatic retraining every 50 new location submissions
- **Output**: Binary classification (normal/anomaly)

### Model Persistence
- Models are saved as pickle files (`anomaly_model.pkl`, `scaler.pkl`)
- Automatic loading on startup
- Fallback training with dummy data if insufficient historical data

## Security Features

- **CORS**: Enabled for cross-origin requests (configure for production)
- **Data Validation**: Pydantic models ensure data integrity
- **Error Handling**: Comprehensive exception handling
- **UUID**: Cryptographically secure identifiers

## Testing

Run the test script to verify all endpoints:

```bash
python test_api.py
```

This will test:
1. Tourist registration
2. Geofence creation
3. Location submission (safe and dangerous)
4. SOS alert creation
5. Alert retrieval
6. Heatmap data
7. Tourist details

## Production Deployment

### Environment Variables
Consider setting these for production:
- `CORS_ORIGINS`: Specific allowed origins instead of "*"
- `CSV_DIRECTORY`: Custom directory for CSV files
- `ML_RETRAIN_INTERVAL`: Custom retraining frequency

### Performance Considerations
- For high-volume deployments, consider migrating to a proper database
- Implement caching for geofence checks
- Add rate limiting for API endpoints
- Use async file operations for better performance

### Monitoring
- Add logging for all operations
- Implement health check endpoints
- Monitor ML model performance
- Set up alerts for system failures

## API Architecture

```
FastAPI Application
├── Pydantic Models (Data Validation)
├── CSV Utilities (Data Persistence)
├── Geofencing Engine (Shapely)
├── ML Pipeline (Scikit-learn)
├── Alert System
└── CORS Middleware
```

## Error Handling

The API includes comprehensive error handling:
- **404**: Resource not found
- **422**: Validation errors
- **500**: Internal server errors

All errors return structured JSON responses with appropriate HTTP status codes.

---

**Built for Smart India Hackathon 2025** 🇮🇳

For questions or support, please refer to the API documentation at `/docs` when the server is running.