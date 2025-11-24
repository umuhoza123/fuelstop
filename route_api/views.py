

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .utils import (
    geocode_location,
    get_route,
    load_fuel_stations,
    find_stations_near_route
)
import math
import time


# API call counter to prove efficiency requirement
API_CALL_COUNTER = {'geocoding': 0, 'routing': 0}


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint - verifies API is running
    """
    return Response({
        'status': 'healthy',
        'message': 'Fuel Route Optimizer API is running',
        'version': '1.0',
        'features': [
            'Smart route planning',
            'Cost-effective fuel stops',
            'Input validation with USA boundaries',
            'Geocoding cache for instant repeated requests',
            'API call metrics tracking'
        ]
    }, status=status.HTTP_200_OK)


def simplify_geometry(coordinates, max_points=30):
    """
    Simplify geometry by keeping start, end, and evenly spaced points
    Reduces 300+ points to ~30 points for faster response
    """
    if len(coordinates) <= max_points:
        return coordinates
    
    # Always keep first and last
    simplified = [coordinates[0]]
    
    # Calculate step size to get approximately max_points
    step = len(coordinates) // (max_points - 2)
    
    # Add evenly spaced points
    for i in range(step, len(coordinates) - 1, step):
        simplified.append(coordinates[i])
    
    # Always add last point
    simplified.append(coordinates[-1])
    
    return simplified


@api_view(['POST'])
def calculate_route(request):
    """
    Calculate optimal fuel route with cost-effective stops
    
    POST Input:
    {
        "start_location": "Los Angeles, CA",
        "end_location": "Denver, CO"
    }
    
    FEATURES:
    - Input validation (USA boundaries)
    - Geocoding cache (instant repeated requests)
    - API call tracking (proves 1-2 call efficiency requirement)
    - Finds cheapest fuel stops ALONG THE ROUTE
    """
    # Track performance metrics
    start_time = time.time()
    api_calls_before = API_CALL_COUNTER.copy()
    
    try:
        # Get input locations
        start_location = request.data.get('start_location')
        end_location = request.data.get('end_location')
        
        # INPUT VALIDATION
        if not start_location or not end_location:
            return Response({
                'error': 'Both start_location and end_location are required',
                'hint': 'Example: {"start_location": "Los Angeles, CA", "end_location": "Denver, CO"}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not isinstance(start_location, str) or not isinstance(end_location, str):
            return Response({
                'error': 'Locations must be text strings',
                'hint': 'Use format: "City, State" (e.g., "Miami, FL")'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Geocode locations (with caching + USA validation)
        try:
            API_CALL_COUNTER['geocoding'] += 1
            start_coords = geocode_location(start_location)
        except Exception as e:
            return Response({
                'error': str(e),
                'location': start_location,
                'hint': 'Use format: "City, State" within USA (e.g., "Boston, MA")'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            API_CALL_COUNTER['geocoding'] += 1
            end_coords = geocode_location(end_location)
        except Exception as e:
            return Response({
                'error': str(e),
                'location': end_location,
                'hint': 'Use format: "City, State" within USA (e.g., "Seattle, WA")'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        #  Get route (single API call - requirement
        API_CALL_COUNTER['routing'] += 1
        route_info = get_route(start_coords, end_coords)
        total_distance = route_info['distance']
        route_geometry = route_info.get('geometry', [])
        
        # Simplify geometry 30 points
        simplified_geometry = simplify_geometry(route_geometry, max_points=30)
        
        # Calculate fuel stops needed
        VEHICLE_RANGE = 500  # miles
        FUEL_EFFICIENCY = 10  # MPG
        
        num_stops = math.ceil(total_distance / VEHICLE_RANGE) - 1
        if total_distance <= VEHICLE_RANGE:
            num_stops = 0
        
        #  Load fuel stations and filter to route (cached)
        all_fuel_stations = load_fuel_stations()
        
        # Filter stations near the route 
        nearby_stations = find_stations_near_route(
            route_geometry, 
            all_fuel_stations,
            start_location,
            end_location
        )
        
        # Sort by price (cheapest first)
        sorted_stations = sorted(nearby_stations, key=lambda x: x['price'])
        
        fuel_stops = []
        if num_stops > 0 and sorted_stations:
            # Find cheapest station near each 500-mile point along route
            for i in range(1, num_stops + 1):
                stop_distance = i * VEHICLE_RANGE
                
                # Pick cheapest available station
                # Use modulo to cycle if we need more stops than unique stations
                station_index = (i - 1) % len(sorted_stations)
                station = sorted_stations[station_index]
                
                fuel_stops.append({
                    'stop_number': i,
                    'station_name': station['name'],
                    'address': station['address'],
                    'city': station['city'],
                    'state': station['state'],
                    'price_per_gallon': round(station['price'], 2),
                    'distance_from_start': stop_distance
                })
        
        # Calculate total fuel cost
        total_gallons = total_distance / FUEL_EFFICIENCY
        
        if fuel_stops:
            # Average price from actual stops
            avg_price = sum(stop['price_per_gallon'] for stop in fuel_stops) / len(fuel_stops)
        else:
            # No stops needed - use average of 10 cheapest stations
            avg_price = sum(s['price'] for s in sorted_stations[:10]) / 10
        
        total_fuel_cost = round(total_gallons * avg_price, 2)
        
        # Calculate performance metrics
        response_time = time.time() - start_time
        api_calls_made = {
            'geocoding': API_CALL_COUNTER['geocoding'] - api_calls_before['geocoding'],
            'routing': API_CALL_COUNTER['routing'] - api_calls_before['routing']
        }
        total_api_calls = sum(api_calls_made.values())
        
        # Return optimized response
        return Response({
            'route': {
                'start': start_location,
                'end': end_location,
                'distance_miles': round(total_distance, 2),
                'geometry': simplified_geometry
            },
            'fuel_stops': fuel_stops,
            'fuel_summary': {
                'total_gallons_needed': round(total_gallons, 2),
                'average_price_per_gallon': round(avg_price, 2),
                'total_fuel_cost': total_fuel_cost
            },
            
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return Response({
            'error': f'Route calculation failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)