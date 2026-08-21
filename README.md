# Spice Finder

UQCS hackathon project — find spicy restaurants, see a spice heat-map by
area, rate dishes, and brag about your tolerance.

## Stack

- **Backend:** Flask (JSON API only), SQLite via Flask-SQLAlchemy
- **Frontend:** React + Vite
- **Map:** Leaflet.js + react-leaflet
- **Data:** Google Places API + a Claude API pass for spice-mention
  classification

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

## Project layout

```
backend/
  app.py          entry point — creates the Flask app, registers routes
  config.py       loads .env, central place for all settings
  models.py       SQLAlchemy database models (Restaurant, Rating, User...)
  requirements.txt
  .env.example    template for your .env — copy it, don't commit the real one

frontend/
  src/App.jsx     root React component
  src/main.jsx    mounts App into the page
  vite.config.js  dev server config, incl. the /api proxy to Flask
```
