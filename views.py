from flask import render_template, current_app, request, redirect, url_for
from itucsdb1973.data_model import Movie, Language, Country, Company, Genre


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
        form_language = request.form["language"]
        language = Language(form_language)
        db.add_item(language)
        return redirect("/")
    
def country_page():
    db = current_app.config["db"]
    if request.method == "GET":
        return render_template("country_page.html")
    else:
        form_country = request.form["country"]
        country = Country(form_country)
        db.add_item(country)
        return redirect("/")
    
def company_page():
    db = current_app.config["db"]
    if request.method == "GET":
        return render_template("company_page.html")
    else:
        form_company = request.form["company"]
        company = Company(form_company)
        db.add_item(company)
        return redirect("/")
    
def addGenre_page():
    db = current_app.config["db"]
    if request.method == "GET":
        return render_template("addGenre_page.html")
    else:
        form_genre = request.form["genre"]
        genre = Genre(form_genre)
        db.add_item(genre)
        return redirect("/")

def addMovie_page():
    db = current_app.config["db"]
    if request.method == "GET":
        return render_template("addMovie_page.html")
    else:
        form_movie = request.form["movie"]
        movie = Movie(form_movie)
        db.add_item(movie)
        return redirect("/")

