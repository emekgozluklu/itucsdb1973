import views
from flask import Flask
from flask_login import LoginManager
from itucsdb1973.db_handler import DBClient
from itucsdb1973.data_model import get_user
import dbinit

lm = LoginManager()


@lm.user_loader
def load_user(user_id):
    return get_user(user_id)


def create_app():
    app = Flask(__name__)
    gp = ["GET", "POST"]
    app.config.from_object("settings.Config")
    app.add_url_rule("/", view_func=views.home)
    app.add_url_rule("/search_movie", view_func=views.search_movie, methods=gp)
    app.add_url_rule("/discover", view_func=views.discover, methods=gp)
    app.add_url_rule("/notifications", view_func=views.notifications)
    app.add_url_rule("/profile", view_func=views.profile)
    app.add_url_rule("/edit_profile", view_func=views.edit_profile, methods=gp)
    app.add_url_rule("/delete_profile", view_func=views.delete_profile)
    app.add_url_rule("/add_comment/<int:movie_id>",
                     view_func=views.add_comment,
                     methods=["POST"])
    app.add_url_rule("/delete_comment/<int:movie_id>/",
                     view_func=views.delete_comment,
                     methods=["POST"])
    app.add_url_rule("/toggle_pin_comment/<int:movie_id>",
                     view_func=views.toggle_pin, methods=["POST"])
    app.add_url_rule("/movie/<int:movie_id>", view_func=views.movie,
                     methods=gp)
    app.add_url_rule("/add_movie", view_func=views.add_movie, methods=gp)
    app.add_url_rule("/add/<string:item>",
                     view_func=views.add_single_field_item, methods=gp)
    app.add_url_rule("/login", view_func=views.login, methods=gp)
    app.add_url_rule("/logout", view_func=views.logout)
    app.add_url_rule("/signup", view_func=views.signup, methods=gp)
    lm.init_app(app)
    lm.login_view = "login_page"

    db_url = app.config["DATABASE_URL"]
    db = DBClient(db_url)
    dbinit.initialize(db_url)
    db.check_tables()
    app.config["db"] = db
    return app


app = create_app()
if __name__ == "__main__":
    app.run(host="0.0.0.0")
