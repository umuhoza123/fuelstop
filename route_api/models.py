from django.db import models


class Route(models.Model):
    """Store route calculation results"""
    start_location = models.CharField(max_length=200)
    end_location = models.CharField(max_length=200)
    total_distance = models.FloatField()  # in miles
    total_fuel_cost = models.FloatField()  # in USD
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Route: {self.start_location} → {self.end_location}"


class FuelStop(models.Model):
    """Store recommended fuel stops for a route"""
    route = models.ForeignKey(Route, related_name='fuel_stops', on_delete=models.CASCADE)
    stop_number = models.IntegerField()
    station_name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    price_per_gallon = models.FloatField()
    distance_from_start = models.FloatField()  # in miles
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['route', 'stop_number']
    
    def __str__(self):
        return f"Stop {self.stop_number}: {self.station_name}"