from flask import render_template, current_app, request, redirect, url_for, \
    flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import abort

import itucsdb1973.data_model as data_model
from itucsdb1973.data_model import get_user
from forms import LoginForm, RegisterForm, ProfileForm
from passlib.hash import pbkdf2_sha256 as hasher
from itucsdb1973.db_handler import NotUniqueError


def home():
    return render_template("home_page.html")


def search_movie():
    db = current_app.config["db"]
    genres = db.select("movie_genre join genre",
                       ("id", "name", "count(name)"),
                       on_conditions="genre_id=id",
                       group_by="name, genre.id",
                       order_by="count desc"
                       )
    if request.method == "GET":
        return render_template("search_page.html", genres=genres)
    else:
        genre_ids = request.form.getlist("genre_id")
        print(genre_ids)
        film_name = request.form.get("search_query")
        print("film_name", repr(film_name))
        if not genre_ids:
            return render_template("search_page.html", genres=genres)

        place_holder = ", ".join(str(id_) for id_ in genre_ids)
        columns = "title, release_date, language, overview"
        query = f"""SELECT DISTINCT id, {columns} FROM movie JOIN movie_genre 
                            ON id=movie_id 
                            WHERE 
                                genre_id in ({place_holder}) and 
                                title LIKE '%{film_name}'"""
        print(query)
        movies = []
        for row in db._execute(query):
            id_, *datum = row
            movies.append(((id_,),
                           data_model.Movie.from_sql_data(columns.split(", "),
                                                          datum)))

        if not movies:
            return render_template("placeholder.html",
                                   text="No movies matching with specified criteria")
        return render_template("discover_page.html", movies=movies)


def discover():
    db = current_app.config["db"]
    if request.method == "GET":
        movies = db.get_items(data_model.Movie)
        return render_template("discover_page.html", movies=movies)
    else:
        if not current_user.is_admin:
            abort(401)
        movie_key = request.form.get("movie_key")
        db.delete_items(data_model.Movie, id=movie_key)
        return redirect(url_for("discover"))


def movie(movie_id):
    db = current_app.config["db"]
    if request.method == "GET":
        _, movie = db.get_item(data_model.Movie, id=movie_id)
        movie_genres = db.select("movie_genre join genre", ("name",),
                                 on_conditions="genre_id=id",
                                 movie_id=movie_id)
        movie_genres = [id[0] for id in movie_genres]
        pinned_comments = db.get_items(data_model.Comment, is_pinned=True)
        pinned_comments = [(id_, comment) for id_, comment in pinned_comments
                           if comment.movie_id == movie_id]
        regular_comments = db.get_items(data_model.Comment, is_pinned=False)
        regular_comments = [(id_, comment) for id_, comment in regular_comments
                            if comment.movie_id == movie_id]
        genres = db.get_items(data_model.Genre)
        return render_template("movie_page.html",
                               movie=movie, movie_genres=movie_genres,
                               genres=genres, pinned_comments=pinned_comments,
                               regular_comments=regular_comments)
    else:
        if not current_user.is_admin:
            abort(401)
        movie = data_model.Movie(False, **request.form)
        movie_id = db.update_items(movie, id=movie_id)[0][0]
        genre_ids = request.form.get("genres")
        db.delete_rows("movie_genre", returning="", movie_id=movie_id)
        for genre_id in genre_ids:
            db.insert_values("movie_genre", movie_id=movie_id,
                             genre_id=genre_id, returning="")

        movie_genres = db.select("movie_genre join genre", ("name",),
                                 on_conditions="genre_id=id",
                                 movie_id=movie_id)
        movie_genres = [id[0] for id in movie_genres]
        genres = db.get_items(data_model.Genre)
        return render_template("movie_page.html",
                               movie=movie, movie_genres=movie_genres,
                               genres=genres)


@login_required
def profile():
    return render_template("profile_page.html", user=current_user)


# TODO: Show form with pre
def edit_profile():
    user = get_user(current_user.id)
    form = ProfileForm(request.form, bio=user.bio, email=user.email)
    if form.validate_on_submit():
        user.bio = form.data["bio"]
        user.email = form.data["email"]
        db = current_app.config["db"]
        try:
            db.update_items(user, id=current_user.id)
        except NotUniqueError as e:
            # FIXME: Show an error message to user
            raise e
        return redirect(url_for("profile"))
    return render_template("edit_profile_page.html", form=form)


def delete_profile():
    db = current_app.config["db"]
    id = current_user.id
    logout_user()
    db.delete_items(data_model.UserM, id=id)
    return redirect(url_for("home"))


def add_movie():
    if not current_user.is_admin:
        abort(401)
    db = current_app.config["db"]
    if request.method == "GET":
        genres = db.get_items(data_model.Genre)
        return render_template("add_movie_page.html", genres=genres)
    else:
        movie = data_model.Movie(False, **request.form)
        movie_id = db.add_item(movie)[0][0]
        genre_ids = request.form.getlist("genres")
        for genre_id in genre_ids:
            db.insert_values("movie_genre", movie_id=movie_id,
                             genre_id=genre_id, returning="")

        return redirect("/")


# TODO: Return error page on fail
def add_single_field_item(item):
    if not current_user.is_admin:
        abort(401)
    db = current_app.config["db"]
    class_ = getattr(data_model, item.title())
    items = db.get_items(class_)
    item_names = [item.name for _, item in items]
    if request.method == "GET":
        return render_template("add_single_field_item_page.html", item=item,
                               items=items)
    else:
        item_name = request.form[item].title()
        if item_name in item_names:
            flash(f"{item.title()}: {item_name} already exists")
        else:
            obj = class_(item_name)
            db.add_item(obj)
            flash(f"{item.title()}: {item_name} is added")
            items = db.get_items(class_)

        return render_template("add_single_field_item_page.html", item=item,
                               items=items)


# TODO: login page should not be displayed if user is already logged in
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.data["username"]
        user = get_user(username)
        if user is not None:
            password = form.data["password"]
            if hasher.verify(password, user.password):
                login_user(user)
                flash("You have logged in.")
                next_page = request.args.get("next", url_for("home"))
                return redirect(next_page)
        flash("Invalid credentials.")
    return render_template("login_page.html", form=form)


def logout():
    logout_user()
    flash("You have logged out.")
    return redirect(url_for("home"))


def signup():
    form = RegisterForm(request.form)
    db = current_app.config["db"]
    if form.validate_on_submit():
        password = hasher.hash(form.password.data)
        user = data_model.UserM(form.username.data, password,
                                form.email.data, form.profile_photo.data)
        try:
            db.add_item(user)
        except NotUniqueError as e:
            # FIXME: Show an error message to user
            raise e

        return redirect(url_for('login'))
    return render_template('signup_page.html', form=form)


def add_comment(movie_id):
    content = request.form.get("content")
    comment = data_model.Comment(current_user.id, movie_id, content)
    db = current_app.config["db"]
    db.add_item(comment)
    return redirect(url_for("movie", movie_id=movie_id))


def delete_comment(movie_id):
    db = current_app.config["db"]
    comment_id = request.form.get("comment_id")
    db.delete_items(data_model.Comment, id=comment_id)
    return redirect(url_for("movie", movie_id=movie_id))


def toggle_pin(movie_id):
    db = current_app.config["db"]
    comment_id = request.form.get("comment_id")
    _, comment = db.get_item(data_model.Comment, id=comment_id)
    comment.is_pinned = not comment.is_pinned
    db.update_items(comment, id=comment_id)
    return redirect(url_for("movie", movie_id=movie_id))
