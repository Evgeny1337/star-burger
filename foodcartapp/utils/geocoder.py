import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


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

    from foodcartapp.models import PlaceCoordinates

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
