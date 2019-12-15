from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField
from wtforms.validators import Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[Length(min=4, max=25)])
    password = PasswordField("Password", validators=[Length(min=6, max=35)])


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[Length(min=4, max=25)])
    email = StringField("Username", validators=[Length(min=6, max=35)])
    password = PasswordField('New Password', [Length(min=4, max=35),
                                              EqualTo('confirm',
                                                      message='Passwords must match')
                                              ])
    confirm = PasswordField('Repeat Password')
    profile_photo = FileField("Select a file...")
