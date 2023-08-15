import json
from .data_manager_interface import DataManagerInterface
import requests


class JSONDataManager(DataManagerInterface):
    """ Inherits from Storage and implements its functions."""
    def __init__(self, filename):
        self.filename = filename

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
        """ Return all the users."""
        with open("MoviWeb/movies.json", "r") as fileobj:
            users_data = fileobj.read()
            list_all_users = json.loads(users_data)
        return list_all_users

    def get_user_movies(self, user_id):
        """ Return all the movies for a given user."""
        for user in self.get_all_users():
            if user["id"] == int(user_id.strip("<>")):
                return user['movies']
        return None

    def add_user(self, user_id, name):
        """ Add a new user and save it to the database."""
        all_users = self.get_all_users()
        user_exists = False

        for user in all_users:
            if user_id == user["id"]:
                user_exists = True
                break

        if user_exists:
            return "User already exists."
        else:
            new_user = {"id": user_id,
                        "name": name,
                        "movies": []}
            all_users.append(new_user)
            with open("MoviWeb/movies.json", "w") as save_file:
                json_file = json.dumps(all_users)
                save_file.write(json_file)
            return "User added successfully."

    def add_movie(self, user_id, movie_title):
        """ Adds a movie to the user movie list and saves it."""
        list_of_users = self.get_all_users()
        for user in list_of_users:
            if user["id"] == int(user_id.strip("<>")):
                # Get a new movie from API
                new_movie_from_api = self.load_movies_data(movie_title)

                if new_movie_from_api.get("Response") == "False":
                    return None

                new_movie_id = len(user["movies"]) + 1

                new_movie_data = {
                        "id": new_movie_id,
                        "name": new_movie_from_api["Title"],
                        "director": new_movie_from_api["Director"],
                        "year": new_movie_from_api["Year"],
                        "rating": new_movie_from_api["imdbRating"],
                        "image": new_movie_from_api["Poster"]
                }

                user["movies"].append(new_movie_data)

                with open("MoviWeb/movies.json", "w") as save_file:
                    json_file = json.dumps(list_of_users, indent=4)
                    save_file.write(json_file)

                return user["movies"]
        return None

    def delete_movie(self, user_id, movie_id):
        """Deletes a movie from the user's movies list"""
        list_of_users = self.get_all_users()
        for user in list_of_users:
            if user["id"] == int(user_id.strip("<>")):
                movie_to_remove = None
                for movie in user["movies"]:
                    print(movie)
                    if movie["id"] == int(movie_id):
                        movie_to_remove = movie
                        break

                if movie_to_remove:
                    user["movies"].remove(movie_to_remove)
                    print(user["movies"])

                # Save the updated user data to the JSON file
                with open("MoviWeb/movies.json", "w") as save_file:
                    json_file = json.dumps(list_of_users, indent=4)
                    save_file.write(json_file)
                return True
        return False

    def update_movie(self, user_id, movie_id, new_director, new_year, new_rating):
        """Updates a movie from the movies database with a new rating"""
        list_of_users = self.get_all_users()
        for user in list_of_users:
            if user["id"] == int(user_id.strip("<>")):
                for movie in user["movies"]:
                    if movie["id"] == int(movie_id.strip("<>")):
                        movie["director"] = new_director
                        movie["year"] = new_year
                        movie["rating"] = new_rating

                # Save the updated user data to the JSON file
                with open("MoviWeb/movies.json", "w") as save_file:
                    json_file = json.dumps(list_of_users)
                    save_file.write(json_file)
                return True
        return False