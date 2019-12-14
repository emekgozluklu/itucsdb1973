from datetime import date


class Movie:
    _columns = {"budget": int, "imdb_id": str, "original_language": str,
                "overview": str, "popularity": float, "release_date": date,
                "duration": float, "tag_line": str, "revenue": int,
                "title": str, "original_title": str, "vote_average": float,
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
                    if value is None:
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
