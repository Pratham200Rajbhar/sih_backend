# SafeHorizon API - Project Structure

```
SafeHorizon Backend/
├── 📁 config/                    # Configuration files
│   ├── __init__.py
│   └── settings.py               # Application settings and paths
├── 📁 data/                      # CSV datasets (organized)
│   ├── alerts.csv               # Safety alerts
│   ├── geofences.csv            # Restricted area definitions
│   ├── locations.csv            # GPS tracking data
│   └── tourists.csv             # Tourist registrations
├── 📁 models/                    # ML model files
│   ├── anomaly_model.pkl        # Trained IsolationForest model
│   └── scaler.pkl               # Feature scaler
├── 📁 src/                       # Source code modules
│   ├── __init__.py
│   ├── database.py              # CSV operations & data handling
│   ├── geofencing.py            # Geospatial operations
│   ├── ml_engine.py             # Machine learning pipeline
│   └── models.py                # Pydantic data models
├── 📁 tests/                     # Test files
│   └── test_api.py              # API endpoint tests
├── 📁 logs/                      # Application logs (auto-created)
├── 📁 .venv/                     # Virtual environment
├── main.py                       # FastAPI application entry point
├── requirements.txt              # Python dependencies
├── README.md                     # Comprehensive documentation
├── QUICKSTART.md                 # Quick start guide
└── PROJECT_STRUCTURE.md          # This file
```

## 🔧 **Modular Architecture**

### **Core Components:**

#### **1. Configuration Layer** (`config/`)
- **`settings.py`**: Centralized configuration management
  - File paths for data and models
  - API configuration (CORS, host, port)
  - ML parameters (contamination, retrain interval)
  - Logging setup

#### **2. Data Layer** (`src/database.py`)
- **CSV Operations**: Safe read/write operations
- **Data Validation**: JSON serialization handling
- **Error Handling**: Robust file I/O with fallbacks
- **Utilities**: Append, update, and safe conversion functions

#### **3. Business Logic Layer** (`src/`)
- **`models.py`**: Pydantic schemas for API validation
- **`geofencing.py`**: Point-in-polygon detection
- **`ml_engine.py`**: Anomaly detection pipeline

#### **4. API Layer** (`main.py`)
- **FastAPI Application**: Modern async web framework
- **Endpoint Routing**: RESTful API design
- **Middleware**: CORS, error handling
- **Lifespan Management**: Startup/shutdown events

## 📊 **Data Organization**

### **Structured Data Storage:**
```
data/
├── tourists.csv      # Tourist profiles and trip details
├── locations.csv     # Real-time GPS tracking
├── alerts.csv        # Multi-type alerts (SOS, GeoFence, ML)
└── geofences.csv     # Polygon-based restricted areas
```

### **ML Model Storage:**
```
models/
├── anomaly_model.pkl # Trained IsolationForest
└── scaler.pkl        # Feature normalization
```

## 🧪 **Testing Structure**

### **Organized Test Suite:**
```
tests/
└── test_api.py       # Comprehensive endpoint testing
```

**Test Coverage:**
- ✅ Tourist registration
- ✅ Location tracking with geofencing
- ✅ SOS emergency alerts
- ✅ Alert management (CRUD)
- ✅ Data visualization (heatmap)
- ✅ Tourist profile retrieval
- ✅ ML anomaly detection
- ✅ Geofence creation

## 🚀 **Benefits of Organized Structure**

### **1. Maintainability**
- Clear separation of concerns
- Easy to locate and modify specific functionality
- Modular components for independent testing

### **2. Scalability**
- Easy to add new features in appropriate modules
- Database layer can be swapped (CSV → PostgreSQL)
- ML pipeline can be enhanced independently

### **3. Developer Experience**
- Intuitive folder structure
- Clear import statements
- Centralized configuration
- Comprehensive documentation

### **4. Production Readiness**
- Proper logging structure
- Environment-based configuration
- Modular deployment options
- Easy CI/CD integration

## 🔄 **Data Flow**

```
API Request → main.py → src/models.py (validation)
                     ↓
              src/database.py (data persistence)
                     ↓
              src/geofencing.py (location analysis)
                     ↓
              src/ml_engine.py (anomaly detection)
                     ↓
              config/settings.py (configuration)
                     ↓
              Response with processed data
```

## 📈 **Performance Optimizations**

1. **Modular Loading**: Components loaded on-demand
2. **Efficient Data Handling**: Pandas for CSV operations
3. **ML Model Caching**: Persistent model storage
4. **Configuration Caching**: Settings loaded once
5. **Structured Logging**: Performance monitoring ready

## 🔧 **Easy Migration Paths**

### **Database Migration:**
- Replace `src/database.py` with SQL operations
- Keep same interface for seamless transition

### **ML Enhancement:**
- Extend `src/ml_engine.py` with new algorithms
- Add model versioning and A/B testing

### **API Scaling:**
- Add authentication middleware
- Implement rate limiting
- Add caching layers

---

**Status: ✅ Fully Organized & Production Ready**

This modular structure provides a solid foundation for the Smart India Hackathon 2025 demo and future production deployment!