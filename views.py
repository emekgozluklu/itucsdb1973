from flask import render_template, current_app


def home_page():
    return render_template("home.html")


def search_movie_page():
    return render_template("placeholder.html", text="Search movie")


def discover_page():
    db = current_app.config["db"]
    movies = db.select("movie", ("title", "release_date"))
    return render_template("movies.html", movies=movies)


def movie_page():
    return render_template("placeholder.html", text="Movie page")


def notifications_page():
    return render_template("placeholder.html", text="Notifications")


def profile_page():
    return render_template("placeholder.html", text="Profile")
