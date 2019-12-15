from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Length


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[Length(min=4, max=25)])
    password = PasswordField("Password", validators=[Length(min=6, max=35)])
