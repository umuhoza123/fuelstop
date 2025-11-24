import os
import sys
import django

# Add project root to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fuel_optimizer.settings')
django.setup()

# import  module
from route_api.data_loader import fuel_data

# Test loading
print("Testing data loader...")
print(f"Total stations: {len(fuel_data.get_all_stations())}")

print("\nStations in Texas:")
tx_stations = fuel_data.get_stations_by_state('TX')
for station in tx_stations[:3]:
    print(f"  - {station['Truckstop Name']}: ${station['Retail Price']}")

print("\nCheapest stations in Oklahoma:")
ok_cheapest = fuel_data.find_cheapest_near_location('', 'OK', max_results=3)
for station in ok_cheapest:
    print(f"  - {station['Truckstop Name']}: ${station['Retail Price']}")

    print(f"  - {station['Truckstop Name']}: ${station['Retail Price']}")