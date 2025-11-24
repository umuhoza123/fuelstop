import pandas as pd
import os
from django.conf import settings


class FuelDataLoader:
    """Load and process fuel price data from CSV"""
    
    def __init__(self):
        self.csv_path = os.path.join(settings.DATA_DIR, 'fuel_prices.csv')
        self.data = None
        self.load_data()
    
    def load_data(self):
        """Load CSV file into pandas DataFrame"""
        try:
            self.data = pd.read_csv(self.csv_path)
            print(f"✅ Loaded {len(self.data)} fuel stations")
            return True
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def get_stations_by_state(self, state_code):
        """Get all stations in a specific state"""
        if self.data is None:
            return []
        
        stations = self.data[self.data['State'] == state_code]
        return stations.to_dict('records')
    
    def find_cheapest_near_location(self, city, state, max_results=5):
        """Find cheapest stations near a location"""
        if self.data is None:
            return []
        
        # Filter by state
        state_stations = self.data[self.data['State'] == state].copy()
        
        if len(state_stations) == 0:
            return []
        
        # Sort by price
        state_stations = state_stations.sort_values('Retail Price')
        
        # Return top results
        return state_stations.head(max_results).to_dict('records')
    
    def get_all_stations(self):
        """Get all stations as list of dictionaries"""
        if self.data is None:
            return []
        
        return self.data.to_dict('records')


# Create a singleton instance
fuel_data = FuelDataLoader()