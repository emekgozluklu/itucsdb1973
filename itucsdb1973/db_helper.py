import psycopg2 as dbapi2
from itucsdb1973.data_model import Movie


class DBHelper:
    def __init__(self, database_url):
        self.db_url = database_url
        self.conn = dbapi2.connect(database_url)
        self.c = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def create_table(self, table_name, column_spec):
        query = f"CREATE TABLE IF NOT EXISTS {table_name} " \
                f"({', '.join(column_spec)})"
        self._execute(query)

    def insert_values(self, table_name, **kwargs):
        query = f"INSERT INTO {table_name} ({', '.join(kwargs.keys())}) " \
                f"VALUES ({', '.join('%s' for _ in kwargs)})"
        self._execute(query, list(kwargs.values()))

    def delete_rows(self, table_name, **conditions):
        query = f"DELETE FROM {table_name} " + \
                self.get_where_clause(conditions)
        self._execute(query)

    def update_value(self, table_name, key, new_value, **conditions):
        query = f"UPDATE {table_name} SET {key} = '{new_value}'" + \
                self.get_where_clause(conditions)
        self._execute(query)

    def select(self, table_name, columns, **conditions):
        query = f"SELECT {', '.join(columns)} FROM {table_name}" + \
                self.get_where_clause(conditions)
        return self._execute(query)

    def drop_table(self, table_name, delete_option=""):
        self._execute(f"DROP TABLE IF EXISTS {table_name} {delete_option}")

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    @staticmethod
    def get_where_clause(conditions):
        if conditions:
            q = "\nWHERE "
            q += " AND ".join(
                f"{key} = {repr(conditions[key])}" for key in conditions)

            return q
        else:
            return ""

    def _execute(self, query, *args, **kwargs):
        with dbapi2.connect(self.db_url) as conn:
            with conn.cursor() as cursor:
                if args and not kwargs:
                    print(query, args)
                    cursor.execute(query, *args)
                elif kwargs and not args:
                    print(query, kwargs)
                    cursor.execute(query, kwargs)
                elif not (args or kwargs):
                    print(query)
                    cursor.execute(query)
                else:
                    raise TypeError("function takes at most 2 arguments")
                try:
                    return cursor.fetchall()
                except dbapi2.ProgrammingError:
                    pass


def check_isinstance(type_, argument_order=1):
    def decorator(function):
        def wrapper(o, *args):
            if isinstance(args[argument_order - 1], type_):
                return function(o, *args)
            else:
                expected = type_.__name__
                actual = type(args[argument_order - 1]).__name__
                raise TypeError(f"must be {expected}, not {actual}")

        return wrapper

    return decorator


class DBClient:
    def __init__(self, database_url):
        self.database_url = database_url

    @check_isinstance(Movie)
    def add_movie(self, movie):
        with DBHelper(self.database_url) as connection:
            connection.insert_values("movie", **movie.__dict__)

    def add_movies(self, movie_container):
        for movie in movie_container:
            self.add_movie(movie)

    @check_isinstance(Movie, 2)
    def update_movie(self, movie_id, new_movie):
        with DBHelper(self.database_url) as connection:
            for key, value in new_movie.__dict__:
                connection.update_value("movie", key, value,
                                        **{"id": movie_id})

    def delete_movie(self, movie_id):
        with DBHelper(self.database_url) as connection:
            connection.delete_rows("movie", **{"id": movie_id})

    def get_movie(self, movie_id, columns=("*",)):
        with DBHelper(self.database_url) as connection:
            return connection.select("movie", columns, **{"id": movie_id})[0]

    def get_movies(self, columns=("*",)):
        with DBHelper(self.database_url) as connection:
            return connection.select("movie", columns)


if __name__ == '__main__':
    m = Movie(**{"title": "the usual suspects", "budget": 34223})
    db = DBClient("postgres://postgres:docker@localhost:5432/postgres")
    db.get_movie(1)
    # db.update_movie(3, 561)
