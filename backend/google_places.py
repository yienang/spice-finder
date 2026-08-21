"""
Thin wrapper around the Google Places API (New) — the HTTP calls needed
to (1) find restaurants near a point, and (2) fetch a restaurant's
reviews. This file is mostly "plumbing": authentication headers and
parsing the JSON Google sends back. The actual spice-detection logic
lives in keyword_filter.py and spice_classifier.py — this file's only
job is getting raw restaurant + review data out of Google.
"""

import requests

from config import Config

PLACES_BASE_URL = "https://places.googleapis.com/v1/places"


def search_nearby_restaurants(latitude, longitude, radius_meters=20000, max_results=20):
    """
    Calls Google's Nearby Search (New) endpoint and returns a list of
    plain dicts, one per restaurant found, with just the fields we
    actually need (Google's raw response has a lot more than this).
    """
    url = f"{PLACES_BASE_URL}:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": Config.GOOGLE_PLACES_API_KEY,
        # The field mask tells Google exactly which fields to send back
        # — it's mandatory (omitting it is an error, not just wasteful),
        # and it also keeps your usage cheaper: you're billed partly
        # based on which fields you ask for, so requesting only what
        # you need matters.
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location",
    }
    body = {
        "includedTypes": ["restaurant"],
        "maxResultCount": max_results,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": radius_meters,
            }
        },
    }

    response = requests.post(url, headers=headers, json=body)
    if not response.ok:
        # requests' raise_for_status() only tells you the status code
        # (e.g. "400 Bad Request"), not WHY — Google puts the actual
        # reason in the response body, so we print that before raising,
        # otherwise you're debugging blind.
        print("Google Places error response:", response.text)
    response.raise_for_status()
    data = response.json()

    places = []
    for place in data.get("places", []):
        places.append({
            "google_place_id": place["id"],
            "name": place["displayName"]["text"],
            "address": place.get("formattedAddress", ""),
            "latitude": place["location"]["latitude"],
            "longitude": place["location"]["longitude"],
        })
    return places


def search_text_restaurants(text_query, latitude, longitude, radius_meters=20000, max_results=10):
    """
    Calls Google's Text Search (New) endpoint — unlike search_nearby_
    restaurants, this searches by a text query (e.g. "Thai restaurant
    in Brisbane") rather than just "anything classified as a restaurant
    near this point." This matters for us specifically: plain nearby
    search ranks by general prominence, which surfaces big well-known
    venues (hotels, McDonald's, tourist spots) over smaller places that
    actually specialize in a spicy cuisine. A targeted text query gets
    us restaurants actually relevant to what we're looking for.
    """
    url = f"{PLACES_BASE_URL}:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": Config.GOOGLE_PLACES_API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location",
    }
    body = {
        "textQuery": text_query,
        "locationBias": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": radius_meters,
            }
        },
        "pageSize": max_results,
    }

    response = requests.post(url, headers=headers, json=body)
    if not response.ok:
        print("Google Places error response:", response.text)
    response.raise_for_status()
    data = response.json()

    places = []
    for place in data.get("places", []):
        places.append({
            "google_place_id": place["id"],
            "name": place["displayName"]["text"],
            "address": place.get("formattedAddress", ""),
            "latitude": place["location"]["latitude"],
            "longitude": place["location"]["longitude"],
        })
    return places


def get_place_reviews(google_place_id):
    """
    Fetches reviews for one restaurant (Google caps this at 5 reviews
    per place, and always the ones it considers "most relevant" — you
    don't get to choose which 5). Returns just a plain list of review
    text strings, since that's all our spice-detection code needs.
    """
    url = f"{PLACES_BASE_URL}/{google_place_id}"
    headers = {
        "X-Goog-Api-Key": Config.GOOGLE_PLACES_API_KEY,
        "X-Goog-FieldMask": "id,displayName,reviews",
    }

    response = requests.get(url, headers=headers)
    if not response.ok:
        print("Google Places error response:", response.text)
    response.raise_for_status()
    data = response.json()

    reviews = data.get("reviews", [])
    # Each review's text comes back as {"text": {"text": "...", "languageCode": "en"}}
    # — a nested object rather than a plain string, so we unwrap it here.
    return [r["text"]["text"] for r in reviews if "text" in r]
