from flask_sqlalchemy import SQLAlchemy
from .data_manager_interface import DataManagerInterface
import requests
import json

db = SQLAlchemy()


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db):
        self.db = db

    def load_movies_data(self, title):
        """Load movies from the api link when a title is input."""
        API_KEY = "cfb1ce63"
        API_MOVIE_URL = f"http://www.omdbapi.com/?t={title}&apikey={API_KEY}"

        try:
            res = requests.get(API_MOVIE_URL)
            res.raise_for_status()  # Raise an exception for HTTP errors
            movies_data = json.loads(res.text)
            print(movies_data)
            return movies_data
        except requests.exceptions.RequestException as e:
            print("Request Error:", e)
            return None

    def get_all_users(self):
        users = User.query.all()
        return users

    def get_user_movies(self, user_id):
        user = User.query.get(user_id)
        if user:
            movies = user.favorites
        else:
            movies = []
        return movies

    def add_user(self, user_id, name, email):
        new_user = User(id=user_id, username=name, email=email)
        self.db.session.add(new_user)
        self.db.session.commit()

    def add_movie(self, user_id, movie_title):
        user = User.query.get(user_id)
        if user:
            new_movie = Movie(title=movie_title, user=user)
            self.db.session.add(new_movie)
            self.db.session.commit()

    def update_movie(self, user_id, movie_id, new_director, new_year, new_rating):
        existing_movie = Movie.query.get(movie.id)
        if existing_movie:
            # Update the attributes of the existing movie with the new values
            existing_movie.title = movie.title
            existing_movie.genre = movie.genre
            self.db.session.commit()

    def delete_movie(self, user_id, movie_id):
        movie_to_delete = Movie.query.get(movie_id)
        if movie_to_delete:
            self.db.session.delete(movie_to_delete)
            self.db.session.commit()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    favorites = db.relationship('Movie', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Movie {self.title}>'