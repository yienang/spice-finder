"""
Entry point for the Flask backend.

Run it with:  python app.py
It'll start a dev server at http://localhost:5000
"""

import os

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from config import Config
from models import db, Restaurant, Rating, User
from spice_score import compute_blended_score

# Where the built React app lives once you run `npm run build` in
# frontend/ — Vite outputs static HTML/CSS/JS into a "dist" folder.
# Locally you never hit this (the Vite dev server on :5173 handles the
# frontend, proxying /api calls over to this Flask server on :5000), but
# in production there's no separate dev server — this Flask app is the
# ONLY thing running, so it needs to serve those static files itself,
# in addition to answering the /api/* routes it already does.
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")


def create_app():
    """
    We wrap app setup in a function (an "application factory") rather
    than creating the Flask app directly at the top of the file. This is
    a common Flask pattern — it makes it possible to create multiple
    instances of the app later (e.g. one for running tests, one for real
    use) with different configs, without duplicating this setup code.
    For a hackathon this benefit is minor, but it's the standard pattern
    you'll see in every Flask tutorial, so worth getting used to now.
    """
    app = Flask(__name__, static_folder=FRONTEND_DIST, static_url_path="")
    app.config.from_object(Config)

    CORS(app)

    db.init_app(app)

    # This used to only run inside `if __name__ == "__main__":` at the
    # bottom of this file — which only executes when you run `python
    # app.py` directly. In production we run this app via gunicorn
    # instead (a production-grade server), which imports `app` without
    # ever hitting that block, so table creation would silently never
    # happen. Moving it here means it runs no matter how the app starts.
    with app.app_context():
        db.create_all()

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "message": "Spice Finder API is running"})

    @app.route("/api/restaurants")
    def list_restaurants():
        restaurants = Restaurant.query.all()
        results = [
            {
                "id": r.id,
                "name": r.name,
                "address": r.address,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "spice_score": compute_blended_score(r),
                "rating_count": len(r.ratings),
            }
            for r in restaurants
        ]
        return jsonify(results)

    @app.route("/api/ratings", methods=["POST"])
    def create_rating():
        data = request.json

        spice_rating = data.get("spice_rating")
        restaurant_id = data.get("restaurant_id")
        nickname = data.get("nickname")
        note = data.get("note")

        if spice_rating not in [1, 2, 3, 4, 5]:
            return jsonify({"error": "spice_rating must be between 1 and 5"}), 400

        restaurant = Restaurant.query.get(restaurant_id)
        if restaurant is None:
            return jsonify({"error": "no restaurant with that id"}), 400

        user = User.query.filter_by(nickname=nickname).first()
        if user is None:
            user = User(nickname=nickname)
            db.session.add(user)
            db.session.commit()

        rating = Rating(spice_rating=spice_rating, note=note, restaurant=restaurant, user=user)
        db.session.add(rating)
        db.session.commit()

        return jsonify({
            "id": rating.id,
            "nickname": user.nickname,
            "restaurant_id": rating.restaurant_id,
            "spice_rating": rating.spice_rating,
            "note": rating.note,
            "created_at": rating.created_at,
        }), 201

    @app.route("/api/restaurants/<int:restaurant_id>")
    def get_restaurant(restaurant_id):
        restaurant = Restaurant.query.get(restaurant_id)
        if restaurant is None:
            return jsonify({"error": "no restaurant with that id"}), 404

        return jsonify({
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "latitude": restaurant.latitude,
            "longitude": restaurant.longitude,
            "spice_score": compute_blended_score(restaurant),
            "rating_count": len(restaurant.ratings),
            "ratings": [
                {
                    "spice_rating": r.spice_rating,
                    "note": r.note,
                    "created_at": r.created_at,
                    "nickname": r.user.nickname,
                }
                for r in restaurant.ratings
            ],
        })

    @app.route("/api/leaderboard")
    def leaderboard():
        users = User.query.all()

        results = []
        for user in users:
            if not user.ratings:
                continue

            rating_count = len(user.ratings)

            total = 0
            for r in user.ratings:
                total += r.spice_rating
            average_spice = total / rating_count

            results.append({
                "nickname": user.nickname,
                "rating_count": rating_count,
                "average_spice": average_spice,
            })

        results.sort(key=lambda x: x["rating_count"], reverse=True)

        return jsonify(results)

    # Everything below /api/* falls through to here — this is what makes
    # visiting the site's plain URL (e.g. "/", or "/whatever-the-frontend-
    # thinks-the-path-is") return the React app's index.html instead of a
    # 404. React then takes over from there entirely in the browser.
    # Flask matches more specific routes (like /api/health above) before
    # falling back to a catch-all like this one, regardless of the order
    # they're defined in, so this doesn't interfere with the API routes.
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        static_file_path = os.path.join(app.static_folder, path)
        if path and os.path.exists(static_file_path):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
