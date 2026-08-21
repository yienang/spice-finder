"""
Run this file directly to populate your database with real Brisbane
restaurants:

    python seed_restaurants.py

For each restaurant Google Places finds nearby, this pulls its reviews,
runs the cheap keyword filter first, and only calls Claude (the slower,
paid step) for restaurants that actually passed the filter — no point
spending an LLM call on a restaurant where zero reviews even mention
spice.
"""

from app import app
from models import db, Restaurant
from google_places import search_text_restaurants, get_place_reviews
from keyword_filter import review_mentions_spice
from spice_classifier import classify_spice_level

# Brisbane CBD — adjust these if you want a different center point.
BRISBANE_LAT = -27.4705
BRISBANE_LNG = 153.0260
SEARCH_RADIUS_METERS = 20000  # 20km — covers most of inner-to-mid Brisbane

# Plain "restaurant near Brisbane" search ranks by general prominence,
# which surfaces big well-known venues (hotels, McDonald's) over places
# that actually specialize in spicy food. Searching by cuisine directly
# gets us restaurants actually relevant to what this app is for.
CUISINE_QUERIES = [
    "Thai restaurant in Brisbane",
    "Indian restaurant in Brisbane",
    "Mexican restaurant in Brisbane",
    "Sichuan restaurant in Brisbane",
    "Korean restaurant in Brisbane",
    "Malaysian restaurant in Brisbane",
    "Vietnamese restaurant in Brisbane",
    "spicy food restaurant in Brisbane",
]

with app.app_context():
    db.create_all()

    print("Searching Google Places across multiple spicy cuisines...")
    # Run one text search per cuisine, then dedupe by google_place_id —
    # the same restaurant can easily show up in more than one query
    # (e.g. a Thai place might also match "spicy food restaurant").
    # A dict keyed by google_place_id is a simple way to dedupe: adding
    # the same key twice just overwrites with the same value, so we end
    # up with one entry per unique restaurant regardless of how many
    # queries found it.
    places_by_id = {}
    for query in CUISINE_QUERIES:
        results = search_text_restaurants(query, BRISBANE_LAT, BRISBANE_LNG, SEARCH_RADIUS_METERS)
        print(f"  '{query}' -> {len(results)} results")
        for place in results:
            places_by_id[place["google_place_id"]] = place

    places = list(places_by_id.values())
    print(f"Found {len(places)} unique restaurants across all cuisine searches.")

    for place in places:
        # Skip restaurants we've already saved (matched by Google's own
        # unique id) — this lets you safely re-run this script without
        # creating duplicate rows or re-spending API calls on the same
        # restaurant.
        existing = Restaurant.query.filter_by(google_place_id=place["google_place_id"]).first()
        if existing:
            print(f"Skipping {place['name']} (already saved)")
            continue

        print(f"Checking reviews for {place['name']}...")
        reviews = get_place_reviews(place["google_place_id"])
        spicy_reviews = [r for r in reviews if review_mentions_spice(r)]

        llm_spice_score = None
        if spicy_reviews:
            print(f"  -> {len(spicy_reviews)} review(s) mention spice, asking Claude...")
            llm_spice_score = classify_spice_level(spicy_reviews)

        restaurant = Restaurant(
            name=place["name"],
            address=place["address"],
            latitude=place["latitude"],
            longitude=place["longitude"],
            google_place_id=place["google_place_id"],
            llm_spice_score=llm_spice_score,
        )
        db.session.add(restaurant)
        db.session.commit()
        print(f"  Saved with llm_spice_score={llm_spice_score}")

    print("Done!")
