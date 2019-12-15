import views
from flask import Flask
from itucsdb1973.db_handler import DBClient
import dbinit


def create_app():
    app = Flask(__name__)
    gp = ["GET", "POST"]
    app.config.from_object("settings.Config")
    app.add_url_rule("/", view_func=views.home)
    app.add_url_rule("/search_movie", view_func=views.search_movie)
    app.add_url_rule("/discover", view_func=views.discover, methods=gp)
    app.add_url_rule("/notifications", view_func=views.notifications)
    app.add_url_rule("/profile", view_func=views.profile)
    app.add_url_rule("/movie/<int:movie_key>", view_func=views.movie)
    app.add_url_rule("/add_movie", view_func=views.add_movie, methods=gp)
    app.add_url_rule("/add/<string:item>",
                     view_func=views.add_single_field_item, methods=gp)
    db_url = app.config["DATABASE_URL"]
    db = DBClient(db_url)
    dbinit.initialize(db_url)
    db.check_tables()
    app.config["db"] = db
    return app


app = create_app()
if __name__ == "__main__":
    app.run(host="0.0.0.0")
