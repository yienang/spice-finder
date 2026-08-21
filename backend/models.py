"""
Database models will live here.

We're leaving this mostly empty for now — designing Restaurant, Rating,
and User as SQLAlchemy models is the next task, and it's a core learning
piece, so we'll build it together rather than have it generated wholesale.

For now this just creates the `db` object that both app.py and the
(future) model classes need to share.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ratings = db.relationship("Rating", backref="user")

class Restaurant(db.Model):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    google_place_id = db.Column(db.String(255), unique=True, nullable=False)
    llm_spice_score = db.Column(db.Float, nullable=True)
    ratings = db.relationship("Rating", backref="restaurant")

class Rating(db.Model):
    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True)
    spice_rating = db.Column(db.Integer(), nullable=False)
    note = db.Column(db.Text())
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)