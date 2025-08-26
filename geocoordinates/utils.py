import requests
from django.conf import settings
from .models import PlaceCoordinates
from django.core.exceptions import ObjectDoesNotExist
from geopy.distance import geodesic

def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return float(lat), float(lon)


def get_coordinates(address):
    if not settings.YANDEX_GEOCODER_API_KEY:
        return None

    try:
        place_coords = PlaceCoordinates.objects.get(address=address)
        if not place_coords.is_expired():
            return (place_coords.lat, place_coords.lon)
    except ObjectDoesNotExist:
        pass

    try:
        coordinates = fetch_coordinates(settings.YANDEX_GEOCODER_API_KEY, address)
        if coordinates:
            lat, lon = coordinates
            PlaceCoordinates.objects.update_or_create(
                address=address,
                defaults={'lat': lat, 'lon': lon}
            )
            return coordinates
        return None

    except requests.RequestException as e:
        return None


def calculate_distance(coord1, coord2):
    if not coord1 or not coord2:
        return None

    try:
        distance_km = geodesic(coord1, coord2).kilometers
        return round(distance_km, 1)
    except (ValueError, TypeError):
        return None
