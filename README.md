# Spice Finder 🌶️

UQCS hackathon project — find spicy restaurants around Brisbane, see a
spice heat-map by area, rate dishes yourself, and see who's rated the
most on the leaderboard.

## Features

- **Heat-map + pins:** every restaurant plotted on a Brisbane map, with a
  color-coded heat-map overlay (light orange = mild, maroon = blazing).
  Pins for individual restaurants only appear once you zoom in.
- **Spice ratings:** click any restaurant pin to submit a 1-5 spice
  rating with an optional note.
- **Leaderboard:** a "brag wall" ranking users by how many ratings
  they've submitted, with their average spice rating alongside.
- **Onboarding quiz:** a 3-question quiz on first visit that gauges your
  own spice tolerance.
- **Automated spice scoring:** restaurants are seeded from Google Places,
  their reviews run through a keyword filter, and any review that
  mentions spice gets sent to Claude to judge whether it describes real
  heat and assign a 0-5 score — this is what powers a restaurant's spice
  score before anyone's rated it directly.

## Stack

- **Backend:** Flask (JSON API only), SQLite via Flask-SQLAlchemy
- **Frontend:** React + Vite
- **Map:** Leaflet.js + react-leaflet + leaflet.heat
- **Data:** Google Places API (Text Search) for restaurant discovery +
  reviews, Claude (`claude-haiku-4-5`) for spice classification

## Running it locally

You need two terminals open at once — one for the backend, one for the
frontend.

### 1. Backend (Flask API — port 5000)

```
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in your real API keys
```

You'll need two API keys in `.env`:

- `GOOGLE_PLACES_API_KEY` — from Google Cloud Console (Places API (New)
  enabled, billing set up)
- `ANTHROPIC_API_KEY` — from the Anthropic Console

Then seed the database with real Brisbane restaurants (only needs to be
run once, or again any time you want to refresh the data — it skips
restaurants it's already saved):

```
python seed_restaurants.py
```

This searches 20 different spicy cuisines around Brisbane, dedupes the
results, and for each new restaurant checks its reviews for genuine
spice mentions via Claude. It can take several minutes depending on how
many restaurants come back — that's expected.

Now start the API:

```
python app.py
```

Check it worked: open http://localhost:5000/api/health in a browser —
you should see a small JSON response.

### 2. Frontend (React + Vite — port 5173)

```
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — it should say "Backend status: Spice
Finder API is running" if both servers are up. If it says it can't
reach the backend, make sure the Flask server (step 1) is running.

## API endpoints

| Method | Route                       | What it does                                  |
| ------ | ---------------------------- | ---------------------------------------------- |
| GET    | `/api/health`                | Backend liveness check                        |
| GET    | `/api/restaurants`           | List all restaurants with blended spice score |
| GET    | `/api/restaurants/<id>`      | One restaurant + its ratings                  |
| POST   | `/api/ratings`                | Submit a new rating                           |
| GET    | `/api/leaderboard`           | Users ranked by number of ratings submitted   |

## Project layout

```
backend/
  app.py                entry point — creates the Flask app, registers routes
  config.py              loads .env, central place for all settings
  models.py               SQLAlchemy database models (User, Restaurant, Rating)
  spice_score.py           blends real user ratings with the LLM-derived score
  google_places.py         wrapper around the Google Places API
  keyword_filter.py        cheap first-pass filter for spice-mentioning reviews
  spice_classifier.py      sends flagged reviews to Claude for a 0-5 spice score
  seed_restaurants.py      run this once to populate the database
  requirements.txt
  .env.example             template for your .env — copy it, don't commit the real one

frontend/
  src/App.jsx                       root component — quiz gate, tabs, status check
  src/main.jsx                      mounts App into the page
  src/components/RestaurantMap.jsx  the Leaflet map, pins, and heat-map
  src/components/HeatmapLayer.jsx    the heat-map overlay itself
  src/components/RatingForm.jsx     the rating submission form (in each pin's popup)
  src/components/Leaderboard.jsx    the brag wall table
  src/components/OnboardingQuiz.jsx  the first-visit spice tolerance quiz
  vite.config.js                     dev server config, incl. the /api proxy to Flask
```
