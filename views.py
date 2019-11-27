from flask import render_template, current_app, request, redirect, url_for
from itucsdb1973.data_model import Movie, Language


def home_page():
    return render_template("home.html")


def search_movie_page():
    return render_template("placeholder.html", text="Search movie")


def discover_page():
    db = current_app.config["db"]
    if request.method == "GET":
        movies = db.get_items(Movie, ("title", "release_date"))
        return render_template("movies.html", movies=movies)
    else:
        form_movie_keys = request.form.getlist("movie_keys")
        for form_movie_key in form_movie_keys:
            db.delete_items(Movie, id=form_movie_key)
        return redirect(url_for("discover_page"))


def movie_page(movie_key):
    return render_template("placeholder.html",
                           text=f"Movie page for movie with id {movie_key}")


def notifications_page():
    return render_template("placeholder.html", text="Notifications")


def profile_page():
    return render_template("placeholder.html", text="Profile")


def language_page():
    db = current_app.config["db"]
    if request.method == "GET":
        return render_template("language_page.html")
    else:
        language_name = request.form["language"].title()
        languages = [language.name for _, language in db.get_items(Language)]
        if language_name not in languages:
            language = Language(language_name)
            db.add_item(language)
            return redirect("/")
        return render_template("language_page.html")
