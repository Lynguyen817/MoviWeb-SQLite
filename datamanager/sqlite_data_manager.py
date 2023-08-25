from flask_sqlalchemy import SQLAlchemy
from .data_manager_interface import DataManagerInterface
import requests
import json
#from flask_migrate import Migrate

db = SQLAlchemy()
#migrate = Migrate(db)


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
        """Get all users."""
        users = User.query.all()
        return users

    def get_user_movies(self, user_id):
        """Get all user's favorite movies."""
        user = User.query.get(user_id)
        if user:
            movies = user.favorites
        else:
            movies = []
        return movies

    def add_user(self, user_id, name, email):
        """Add a new user."""
        new_user = User(id=user_id, username=name, email=email)
        self.db.session.add(new_user)
        self.db.session.commit()

    def get_user(self, user_id):
        """Get a specific user by user_id."""
        user = User.query.get(user_id)
        return user

    def delete_user(self, user_id):
        """Delete a user."""
        user_to_delete = User.query.get(user_id)
        if user_to_delete:
            # Clear the user ID from associated movies
            for movie in user_to_delete.favorites:
                movie.user_id = None
                self.db.session.delete(movie)
            self.db.session.delete(user_to_delete)
            self.db.session.commit()
            return True
        else:
            return False

    def add_movie(self, user_id, movie_title):
        """Add a new movie to a user's favorite movies list."""
        user = User.query.get(user_id)
        if user:
            new_movie = Movie(title=movie_title, user=user)
            self.db.session.add(new_movie)
            self.db.session.commit()

    def update_movie(self, user_id, movie_id, new_director, new_year, new_rating):
        """Update an existing movie."""
        existing_movie = Movie.query.get(movie.id)
        if existing_movie:
            # Update the attributes of the existing movie with the new values
            existing_movie.title = movie.title
            existing_movie.genre = movie.genre
            self.db.session.commit()

    def delete_movie(self, user_id, movie_id):
        """Delete a movie from the database."""
        movie_to_delete = Movie.query.get(movie_id)
        if movie_to_delete:
            self.db.session.delete(movie_to_delete)
            self.db.session.commit()


class User(db.Model):
    """Create a user table."""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    favorites = db.relationship('Movie', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Movie(db.Model):
    """Create a movie table."""
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    # poster_url = db.Column(db.String(200))
    # director = db.Column(db.String(120), nullable=False)
    # year = db.Column(db.Integer, nullable=False)
    # rating = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def __repr__(self):
        return f'<Movie {self.title}>'

