from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, TextAreaField
from wtforms.validators import Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[Length(min=4, max=25)])
    password = PasswordField("Password", validators=[Length(min=6, max=35)])


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[Length(min=4, max=25)])
    email = StringField("Email", validators=[Length(min=6, max=35)])
    password = PasswordField('New Password', [Length(min=4, max=35),
                                              EqualTo('confirm',
                                                      message='Passwords must match')
                                              ])
    confirm = PasswordField('Repeat Password')
    profile_photo = FileField("Select a file...")


class ProfileForm(FlaskForm):
    bio = TextAreaField("Bio", validators=[Length(min=1, max=250)])
    email = StringField("Change your email address", validators=[Length(min=6, max=35)])
