from .data_models import *
from .data_manager_interface import DataManagerInterface
import requests
import json


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

    def add_movie(self, user_id, movie_data):
        """Add a new movie to a user's favorite movies list."""
        user = User.query.get(user_id)
        if user:
            new_movie = Movie(
                user=user,
                title=movie_data["Title"],
                poster_url=movie_data["Poster"],
                director=movie_data["Director"],
                year=movie_data["Year"],
                rating=float(movie_data["imdbRating"])
            )
            self.db.session.add(new_movie)
            self.db.session.commit()

    def update_movie(self, user_id, movie_id, new_director, new_year, new_rating):
        """Update an existing movie."""
        existing_movie = Movie.query.get(movie_id)
        if existing_movie:
            # Update the attributes of the existing movie with the new values
            existing_movie.director = new_director
            existing_movie.year = new_year
            existing_movie.rating = new_rating
            self.db.session.commit()
            return True
        else:
            return False

    def delete_movie(self, user_id, movie_id):
        """Delete a movie from the database."""
        movie_to_delete = Movie.query.get(movie_id)
        if movie_to_delete:
            self.db.session.delete(movie_to_delete)
            self.db.session.commit()
            return True
        else:
            return False

    def add_review(self, user_id, movie_id, review_text, rating):
        """Add review to a movie."""
        movie = Movie.query.get(movie_id)
        if movie:
            new_review = Review(user_id=user_id, movie_id=movie_id, review_text=review_text, rating=rating)
            self.db.session.add(new_review)
            self.db.session.commit()
            return True
        else:
            return False

    def user_reviews(self, user_id, movie_id):
        """Show all the reviews of the movie"""
        user = User.query.get(user_id)
        movie = Movie.query.get(movie_id)
        if user and movie:
            reviews = Review.query.filter_by(user_id=user_id, movie_id=movie_id).all()
        else:
            reviews = []
        return reviews
