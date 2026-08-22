from geopy.distance import geodesic

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float: #calculates distance between two points
    return geodesic((lat1, lon1), (lat2, lon2)).km #calculates the real-world distance between two points on the curved surface of the Earth

def implied_speed_kmh(lat1: float, lon1: float, lat2: float, lon2: float, seconds: float) -> float: # how fast travelling
    if seconds <= 0:
        return 0.0
    dist_km = haversine_distance_km(lat1, lon1, lat2, lon2) 
    return dist_km / (seconds / 3600)