import views
from flask import Flask
from itucsdb1973.db_helper import DBHelper


def create_app():
    app = Flask(__name__)
    app.config.from_object("settings")
    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/search_movie", view_func=views.search_movie_page)
    app.add_url_rule("/discover", view_func=views.discover_page)
    app.add_url_rule("/notifications", view_func=views.notifications_page)
    app.add_url_rule("/profile", view_func=views.profile_page)
    db = DBHelper("postgres://postgres:docker@localhost:5432/postgres")
    app.config["db"] = db
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0")
