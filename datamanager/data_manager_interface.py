from abc import ABC, abstractmethod


class DataManagerInterface(ABC):
    """Create an interface."""
    @abstractmethod
    def get_all_users(self):
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        pass

    @abstractmethod
    def add_user(self, user_id, name, email):
        pass

    @abstractmethod
    def add_movie(self, user_id, movie_title):
        pass

    @abstractmethod
    def delete_movie(self, user_id, movie_id):
        pass

    @abstractmethod
    def update_movie(self, user_id, movie_id, new_director, new_year, new_rating):
        pass
