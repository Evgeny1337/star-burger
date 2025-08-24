from geopy.distance import geodesic


def calculate_distance(coord1, coord2):
    if not coord1 or not coord2:
        return None
    try:
        distance_km = geodesic(coord1, coord2).kilometers
        return round(distance_km, 1)
    except (ValueError, TypeError) as e:
        return None
