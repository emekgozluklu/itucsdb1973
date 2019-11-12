from datetime import date


class Movie:
    _columns = {"budget": int, "imdb_id": str, "original_language": str,
                "overview": str, "popularity": float, "release_date": date,
                "duration": int, "tag_line": str, "title": str,
                "original_title": str, "vote_average": float,
                "vote_count": int}

    def __init__(self, column_check_=True, **kwargs):
        for key, value in kwargs.items():
            if key not in self._columns:
                if not column_check_:
                    continue
                raise TypeError(f"'{key}' is an invalid keyword argument for "
                                f"'{self.__class__.__name__}' class")
            elif not isinstance(value, self._columns[key]):
                expected = self._columns[key].__name__
                actual = type(value).__name__
                if value is None:
                    continue
                raise TypeError(f"{key} must be '{expected}' not '{actual}'")
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


class NameOnlyClass:
    def __init__(self, name):
        self.name = name

    @classmethod
    def from_sql_data(cls, column_names, datum):
        return cls(dict(zip(column_names, datum)).get("name"))


class Genre(NameOnlyClass):
    pass


class Company(NameOnlyClass):
    pass


class Country(NameOnlyClass):
    pass


class Language(NameOnlyClass):
    pass
