from flask import Flask, render_template, request, redirect, url_for
from datamanager.sqlite_data_manager import *
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate

app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moviwebapp.db'

db.init_app(app)
with app.app_context():
    db.create_all()

migrate = Migrate(app, db)
data_manager = SQLiteDataManager(db)


@app.route('/')
def home():
    """Returns homepage, alerts error when it's not open."""
    try:
        return render_template("users.html")
    except Exception as e:
        return str(e)


@app.route('/search_movie')
def search_movie():
    """Return a movie that the user searches."""
    title = request.args.get('title')
    movie_data = data_manager.load_movies_data(title)
    print(movie_data)

    if movie_data and movie_data.get('Response') == 'False':
        return "Movie not found", 404

    return render_template('search_movie.html', movie_data=movie_data)


@app.route('/users')
def list_users():
    """Returns a list of users."""
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)


@app.route('/users/<user_id>/movies')
def user_movies(user_id):
    """Return a list of movies for a given user_id."""
    list_of_user_movies = data_manager.get_user_movies(user_id)
    # Check if the list_of_users_movies is None, and if so, set it to an empty list
    if list_of_user_movies is None:
        list_of_user_movies = []

    # Retrieve the new_movie_list from the query parameters if it exists
    new_movies_list = request.args.get('new_movie_list', None)
    if new_movies_list:
        list_of_user_movies.append(new_movies_list)

    return render_template('user_movies.html', user_id=user_id, list_of_user_movies=list_of_user_movies)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Get a new user."""
    users = data_manager.get_all_users()
    if request.method == 'POST':
        # Get user input from the form
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Generate a unique identifier for a new user
        new_user_id = len(users) + 1

        # Add the new user to the data manager
        data_manager.add_user(new_user_id, username, email)
        return redirect(url_for('list_users'))

    # Else, it's GET method
    return render_template('add_user.html')


@app.route('/users/<user_id>/delete_user', methods=['GET', 'POST'])
def delete_user(user_id):
    """Delete a user from the list."""
    user = data_manager.get_user(user_id)
    if request.method == 'POST':
        deleted = data_manager.delete_user(user_id)
        if deleted:
            return redirect(url_for('list_users'))
        else:
            return "User not found"
    return render_template('delete_user.html', user=user)


@app.route('/users/<user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """Search for a movie and add it to a user's favorite movies list."""
    if request.method == 'POST':
        movie_title = request.form.get('title')

        if not movie_title:
            return "Please provide a movie title.", 400

        movie_data = data_manager.load_movies_data(movie_title)

        # Call the add_movie method of the data_manager to add the movie to the user's list
        if movie_data and movie_data.get('Response') == 'True':
            data_manager.add_movie(user_id, movie_data)
            return redirect(url_for('user_movies', user_id=user_id))
        else:
            return "Movie not found", 404

    # It's GET method
    return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<user_id>/delete_movie/<movie_id>', methods=['GET', 'POST'])
def delete_movie(user_id, movie_id):
    """ Delete a movie from the user's favorite movie list"""
    if request.method == 'POST':
        deleted = data_manager.delete_movie(user_id, movie_id)
        if deleted:
            return redirect(url_for('user_movies', user_id=user_id))
        else:
            return "Movie not found"

    # Get the movie data
    list_of_user_movies = data_manager.get_user_movies(user_id)
    movie = next((m for m in list_of_user_movies if m.id == int(movie_id)), None)

    if not movie:
        return "Movie not found"

    # It's a GET request, render the delete page
    return render_template('delete_movie.html', user_id=user_id, movie_id=movie_id, movie=movie)


@app.route('/users/<user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """Update a movie in the user's movie list"""
    if request.method == 'POST':
        new_director = request.form.get('director')
        new_year = request.form.get('year')
        new_rating = request.form.get('rating')
        updated = data_manager.update_movie(user_id, movie_id, new_director, new_year, new_rating)
        if updated:
            return redirect(url_for('user_movies', user_id=user_id))
        else:
            return "Movie not found"

    # Get the movie data
    list_of_users_movies = data_manager.get_user_movies(user_id.strip("<>"))
    movie = next((m for m in list_of_users_movies if m.id == int(movie_id)), None)

    if not movie:
        return "Movie not found"

    # Render the movie update form
    return render_template('edit_movie.html', user_id=user_id, movie=movie)


@app.route('/add_review/<user_id>/<movie_id>', methods=['GET', 'POST'])
def add_review(user_id, movie_id):
    """ Add a review to an existing movie"""
    movie = Movie.query.get(movie_id)
    if request.method == 'POST':
        review_text = request.form.get('review_text')
        rating = float(request.form.get('rating'))

        # Call the add_review method
        added = data_manager.add_review(user_id, movie_id, review_text, rating)
        if added:
            return redirect(url_for('user_reviews', user_id=user_id, movie_id=movie_id))
        else:
            return "Movie not found"

    # It's a GET method, render the review submission form
    return render_template('add_review.html', user_id=user_id, movie_id=movie_id, movie=movie)


@app.route('/user_reviews/<user_id>/<movie_id>')
def user_reviews(user_id, movie_id):
    user = User.query.get(user_id)
    movie = Movie.query.get(movie_id)
    if user:
        reviews = data_manager.user_reviews(user_id, movie_id)
        return render_template('user_reviews.html', user=user, movie=movie, reviews=reviews)
    else:
        return "User or movie not found"


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)

