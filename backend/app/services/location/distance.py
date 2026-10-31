import math
from typing import Optional

# Mean Earth radius in kilometers
EARTH_RADIUS_KM = 6371.0
KM_TO_MILES = 0.621371

PRESET_CITIES = {
    "San Francisco": {"lat": 37.7749, "lng": -122.4194},
    "Bengaluru": {"lat": 12.9716, "lng": 77.5946},
    "Mumbai": {"lat": 19.0760, "lng": 72.8777},
    "New Delhi": {"lat": 28.6139, "lng": 77.2090},
    "Gurugram": {"lat": 28.4595, "lng": 77.0266},
    "New York": {"lat": 40.7128, "lng": -74.0060},
    "London": {"lat": 51.5074, "lng": -0.1278},
    "Tokyo": {"lat": 35.6762, "lng": 139.6503},
    "Paris": {"lat": 48.8566, "lng": 2.3522},
    "Berlin": {"lat": 52.5200, "lng": 13.4050},
    "Toronto": {"lat": 43.6532, "lng": -79.3832},
    "Sydney": {"lat": -33.8688, "lng": 151.2093},
    "Singapore": {"lat": 1.3521, "lng": 103.8198}
}

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great-circle distance between two points on the Earth's surface
    using the spherical Haversine formula.
    
    Formula:
        a = sin²(Δφ/2) + cos(φ1) ⋅ cos(φ2) ⋅ sin²(Δλ/2)
        c = 2 ⋅ atan2( √a, √(1−a) )
        d = R ⋅ c
    where φ is latitude, λ is longitude, and R is Earth's mean radius (6,371 km).
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    distance = EARTH_RADIUS_KM * c
    return round(distance, 2)

def haversine_distance_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance converted to miles."""
    km = haversine_distance_km(lat1, lon1, lat2, lon2)
    return round(km * KM_TO_MILES, 2)

def is_within_radius(lat1: float, lon1: float, lat2: float, lon2: float, radius_km: float) -> bool:
    """Returns True if the distance between two points is within radius_km."""
    return haversine_distance_km(lat1, lon1, lat2, lon2) <= radius_km
