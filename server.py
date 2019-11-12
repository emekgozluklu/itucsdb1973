import views
from flask import Flask
from itucsdb1973.db_handler import DBClient
import dbinit


def create_app():
    app = Flask(__name__)
    GP = ["GET", "POST"]
    app.config.from_object("settings.Config")
    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/search_movie", view_func=views.search_movie_page)
    app.add_url_rule("/discover", view_func=views.discover_page, methods=GP)
    app.add_url_rule("/notifications", view_func=views.notifications_page)
    app.add_url_rule("/profile", view_func=views.profile_page)
    app.add_url_rule("/movie/<int:movie_key>", view_func=views.movie_page)
    db_url = app.config["DATABASE_URL"]
    db = DBClient(db_url)
    dbinit.initialize(db_url)
    app.config["db"] = db
    return app


app = create_app()
if __name__ == "__main__":
    app.run(host="0.0.0.0")
