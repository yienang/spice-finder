"""
Central place for all configuration values.

Why this file exists: instead of scattering os.environ.get(...) calls
across every route file, every setting lives here once. Anything in the
app that needs a config value imports this Config class instead of
touching environment variables directly. If you ever need to add a
"testing" config or a "production" config with different values, this
is the one place you'd extend.
"""

import os
from dotenv import load_dotenv

# load_dotenv() reads the .env file (if present) and copies its
# key=value lines into the process's environment variables, as if you'd
# typed `export GOOGLE_PLACES_API_KEY=...` in the terminal before running
# the app. This runs once, when config.py is first imported.
load_dotenv()


class Config:
    GOOGLE_PLACES_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY")
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

    # SQLALCHEMY_DATABASE_URI is the exact name Flask-SQLAlchemy looks
    # for — not our choice, it's the library's convention.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///spice_finder.db"
    )
    # Turns off a Flask-SQLAlchemy feature we don't need (it tracks every
    # object change for an event system) — it just costs memory otherwise.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
