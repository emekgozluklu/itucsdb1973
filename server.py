import views
from flask import Flask
from itucsdb1973.db_helper import DBHelper
import dbinit


def create_app():
    app = Flask(__name__)
    if app.env == 'production':
        app.config.from_object("settings.ProductionConfig")
    else:
        app.config.from_object("settings.DevelopmentConfig")
    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/search_movie", view_func=views.search_movie_page)
    app.add_url_rule("/discover", view_func=views.discover_page)
    app.add_url_rule("/notifications", view_func=views.notifications_page)
    app.add_url_rule("/profile", view_func=views.profile_page)
    app.add_url_rule("/movie/<int:movie_key>", view_func=views.movie_page)
    db = DBHelper(app.config["DATABASE_URL"])
    dbinit.initialize(db.db_url)
    app.config["db"] = db
    return app


app = create_app()
if __name__ == "__main__":
    app.run(host="0.0.0.0")
