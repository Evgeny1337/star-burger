import requests
from django.conf import settings
from django.core.cache import cache

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

    cache_key = f'geocoder_{address}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        coordinates = fetch_coordinates(settings.YANDEX_GEOCODER_API_KEY, address)
        if coordinates:
            cache.set(cache_key, coordinates, 60 * 60 * 24)
            return coordinates
        return None

    except requests.RequestException as e:
        return None
    except (KeyError, IndexError, ValueError) as e:
        return None
