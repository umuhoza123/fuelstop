# Fuel Route Optimizer API

**Django REST API that calculates optimal fuel stops for truck routes across the USA based on real fuel prices**

##  Key Features

-  **Smart Route Planning** - Calculates optimal driving routes between any two US cities
-  **Cost-Effective Fuel Stops** - Finds cheapest fuel stations along your route
-  **Real-Time Mapping** - Returns GeoJSON coordinates for route visualization
-  **Fast Performance** - Optimized to return results in seconds
- **No API Keys Required** - Uses free OSRM and Nominatim services
-  **8,151 Fuel Stations** - Comprehensive fuel price database from CSV

###  NEW  FEATURES:

-  **Input Validation** - Validates USA boundaries, provides helpful error messages
-  **Geocoding Cache** - Repeated requests are INSTANT (no redundant API calls)



### Installation

```bash
# Clone repository
git clone https://github.com/umuhoza123/fuelstop.git
cd fuelstop

# Install dependencies
pip install -r requirements.txt

# Run server
python manage.py runserver
```

### Test the API

```bash
# Health check
curl http://127.0.0.1:8000/api/health/

# Calculate route
curl -X POST http://127.0.0.1:8000/api/calculate-route/ \
  -H "Content-Type: application/json" \
  -d '{"start_location": "Los Angeles, CA", "end_location": "Denver, CO"}'
```

##  API Endpoints

### 1. Calculate Route (POST)
**Endpoint:** `POST /api/calculate-route/`

**Request Body:**
```json
{
  "start_location": "Los Angeles, CA",
  "end_location": "Denver, CO"
}
```

**Response:**
```json
{
  "route": {
    "start": "Los Angeles, CA",
    "end": "Denver, CO",
    "distance_miles": 1018.79,
    "geometry": [[lon, lat], [lon, lat], ...]
  },
  "fuel_stops": [
    {
      "stop_number": 1,
      "station_name": "7-ELEVEN #218",
      "address": "I-44, EXIT 283 & US-69",
      "city": "Harrold",
      "state": "TX",
      "price_per_gallon": 2.69,
      "distance_from_start": 500.0
    }
  ],
  "fuel_summary": {
    "total_gallons_needed": 101.88,
    "average_price_per_gallon": 2.70,
    "total_fuel_cost": 274.56
  }
 
}
```

## Project Structure


fuel_route_api/
├── route_api/
│   ├── views.py        # Main API endpoint logic
│   ├── utils.py        # Helper functions (geocoding, routing, CSV loader)
│   ├── urls.py         # API route definitions
│   └── apps.py         # Django app configuration
├── data/
│   └── fuel_prices.csv # Fuel station price data
├── fuel_optimizer/
│   ├── settings.py     # Django settings
│   ├── urls.py         # Main URL configuration
│   └── wsgi.py         # WSGI configuration
├── manage.py           # Django management script
└── requirements.txt    # Python dependencies
```

## Technical Details

- **External API:** OpenRouteService (for geocoding and routing)
- **Data Source:** CSV file with 8,151+ fuel stations
- **Optimization:** Selects cheapest fuel stations along route
- **Performance:** Simplified route geometry (50 points) for fast response
- **Range:** Calculates stops every 500 miles
- **Fuel Consumption:** 10 miles per gallon

## Dependencies

- Django 5.2+
- Django REST Framework
- requests

## 🎥 Video Demo

[Watch 5-minute Loom Demo](YOUR_LOOM_LINK_HERE) - Shows API in action with Postman





## 🧪 Testing

Import `Postman_Collection.json` into Postman for pre-configured test cases:
- Short route (Dallas → Houston)
- Medium route (LA → Denver)  
- Long route (NYC → LA)


## Notes

- Requires valid OpenRouteService API key in `utils.py`
- Fuel prices loaded from `data/fuel_prices.csv`
- Route geometry returned for map visualization
- No database required - stateless API
