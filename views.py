from flask import render_template, current_app, request, redirect, url_for, \
    flash
import itucsdb1973.data_model as data_model


def home():
    return render_template("home.html")


def search_movie():
    return render_template("placeholder.html", text="Search movie")


def discover():
    db = current_app.config["db"]
    if request.method == "GET":
        movies = db.get_items(data_model.Movie, ("title", "release_date"))
        return render_template("movies.html", movies=movies)
    else:
        form_movie_keys = request.form.getlist("movie_keys")
        for form_movie_key in form_movie_keys:
            db.delete_items(data_model.Movie, id=form_movie_key)
        return redirect(url_for("discover_page"))


def movie(movie_key):
    return render_template("placeholder.html",
                           text=f"Movie page for movie with id {movie_key}")


def notifications():
    return render_template("placeholder.html", text="Notifications")


def profile():
    return render_template("placeholder.html", text="Profile")


def add_movie():
    db = current_app.config["db"]
    if request.method == "GET":
        return render_template("add_movie_page.html")
    else:
        title = request.form["title"]
        original_title = request.form["original_title"] or None
        budget = int(request.form["budget"] or 0) or None
        duration = int(request.form["duration"] or 0) or None
        vote_average = float(request.form["vote_average"] or 0) or None
        vote_count = int(request.form["vote_count"] or 0) or None
        original_language = request.form["original_language"] or None
        release_date = request.form["release_date"] or None
        popularity = float(request.form["popularity"] or 0) or None
        imdb_id = request.form["imdb_id"] or None
        overview = request.form["overview"] or None
        tag_line = request.form["tag_line"] or None
        movie = data_model.Movie(title=title, original_title=original_title,
                                 budget=budget, duration=duration,
                                 vote_average=vote_average,
                                 vote_count=vote_count,
                                 original_language=original_language,
                                 release_date=release_date,
                                 popularity=popularity, imdb_id=imdb_id,
                                 overview=overview,
                                 tag_line=tag_line)

        db.add_item(movie)
        return redirect("/")


def add_single_field_item(item):
    if request.method == "GET":
        return render_template("add_single_field_item_page.html", item=item)
    else:
        db = current_app.config["db"]
        item_name = request.form[item].title()
        class_ = getattr(data_model, item.title())
        items = [item.name for _, item in db.get_items(class_)]
        if item_name in items:
            flash(f"{item.title()}: {item_name} already exists")
        else:
            obj = class_(item_name)
            db.add_item(obj)
            flash(f"{item.title()}: {item_name} is added")

        return render_template("add_single_field_item_page.html", item=item)
