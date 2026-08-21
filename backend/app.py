"""
Entry point for the Flask backend.

Run it with:  python app.py
It'll start a dev server at http://localhost:5000
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

from config import Config
from models import db, Restaurant, Rating, User
from spice_score import compute_blended_score


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
    app = Flask(__name__)
    app.config.from_object(Config)

    # CORS(app) opens the API to requests from other origins (like your
    # React dev server on a different port). Without this, the browser's
    # "same-origin policy" would silently block fetch() calls from React
    # to Flask, and you'd see a confusing CORS error in the console.
    # For a hackathon, allowing all origins is fine. In a real production
    # app you'd lock this down to your actual frontend's domain.
    CORS(app)

    # Connects the SQLAlchemy `db` object (defined in models.py) to this
    # specific Flask app instance, using the SQLALCHEMY_DATABASE_URI from
    # our Config.
    db.init_app(app)

    @app.route("/api/health")
    def health():
        """
        A trivial endpoint that just confirms the server is up and can
        respond with JSON. Useful for us to check the backend is wired
        correctly before we build anything that depends on it.
        """
        return jsonify({"status": "ok", "message": "Spice Finder API is running"})

    @app.route("/api/restaurants")
    def list_restaurants():
        """
        Returns every restaurant, with its blended spice score, as JSON.
        This is what your React map view will fetch to draw pins + the
        heatmap overlay.
        """
        # Restaurant.query.all() is SQLAlchemy's way of saying "give me
        # every row in the restaurants table, as a list of Restaurant
        # objects." Under the hood this runs `SELECT * FROM restaurants`
        # — you get to think in Python objects instead of writing SQL.
        restaurants = Restaurant.query.all()

        # jsonify() can only turn plain Python data (dicts, lists,
        # strings, numbers) into JSON — it has no idea how to convert a
        # custom Restaurant object on its own. So we build a plain dict
        # for each restaurant ourselves first. This step — turning a
        # database object into a plain dict/JSON-friendly shape — is
        # called "serialization," and you'll do it in every GET route.
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
        data = request.json  # the dict the frontend sent, e.g. {"nickname": "...", "restaurant_id": 1, "spice_rating": 5, "note": "..."}

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
                continue  # skip people who haven't rated anything yet

            # TODO: compute rating_count (how many ratings this user has)
            rating_count = len(user.ratings)

            # TODO: compute average_spice (average of user.ratings' spice_rating values)
            total = 0
            for i in user.ratings:
                total += i.spice_rating
            average_spice = total/rating_count

            results.append({
                "nickname": user.nickname,
                "rating_count": rating_count,      # fill in
                "average_spice": average_spice,     # fill in
            })

        # TODO: sort `results` so the leaderboard is actually ordered —
        # think about whether "most active" or "spiciest tolerance" matters
        # more for a brag wall, and sort by that field. Hint: list.sort(key=..., reverse=True)
        results.sort(key=lambda x: x["rating_count"], reverse=True)

        return jsonify(results)
    
    return app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        # Creates any database tables that don't exist yet, based on
        # whatever model classes have been defined. Right now there are
        # none (models.py is empty), so this does nothing yet — but it
        # will matter as soon as we add Restaurant/Rating/User models.
        db.create_all()

    app.run(debug=True, port=5000)
