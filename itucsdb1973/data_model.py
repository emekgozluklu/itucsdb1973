from datetime import date
from flask import current_app
from flask_login import UserMixin


class UserM(UserMixin):
    def __init__(self, username, password, email, profile_photo,
                 joined_at):
        self.id = username
        self.password = password
        self.email = email
        self.profile_photo = profile_photo
        self.joined_at = joined_at
        self.active = True
        self.is_admin = False

    def get_id(self):
        return self.id

    @property
    def is_active(self):
        return self.active


def get_user(user_id):
    db = current_app.config["db"]
    _, user = db.get_item(UserM, id=user_id)
    return user


class Movie:
    _columns = {"budget": int, "imdb_id": str, "language": str,
                "overview": str, "popularity": float, "release_date": date,
                "duration": float, "tag_line": str, "revenue": int,
                "title": str, "vote_average": float,
                "vote_count": int}

    def __init__(self, column_check_=True, **kwargs):
        for key, value in kwargs.items():
            if key not in self._columns:
                if not column_check_:
                    continue
                raise TypeError(f"'{key}' is an invalid keyword argument for "
                                f"'{self.__class__.__name__}' class")
            elif not isinstance(value, self._columns[key]):
                try:
                    if self._columns[key] is date:
                        value = date.fromisoformat(value)
                    else:
                        value = self._columns[key](value)
                except (ValueError, TypeError):
                    expected = self._columns[key].__name__
                    actual = type(value).__name__
                    if not value:
                        continue
                    raise ValueError(
                        f"{key} must be '{expected}' not '{actual}'")
                else:
                    setattr(self, key, value)
            else:
                setattr(self, key, value)

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            if name in self._columns:
                return None
            raise e

    @classmethod
    def from_sql_data(cls, column_names, datum):
        return cls(False, **dict(zip(column_names, datum)))

    def __repr__(self):
        return f"Movie({', '.join((name + '=' + repr(value)) for name, value in self.__dict__.items())})"


class NameOnlyClass:
    def __init__(self, name):
        self.name = name

    @classmethod
    def from_sql_data(cls, column_names, datum):
        return cls(dict(zip(column_names, datum)).get("name"))

    def __repr__(self):
        return f"{self.__class__.__name__}(name={repr(self.name)})"


class Genre(NameOnlyClass):
    pass


class Company(NameOnlyClass):
    pass


class Country(NameOnlyClass):
    pass


class Language(NameOnlyClass):
    pass
