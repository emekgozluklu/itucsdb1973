import psycopg2 as dbapi2
from functools import wraps
from itucsdb1973.data_model import Movie, Genre


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

    def get_table_names(self):
        rows = self._execute("""SELECT table_name
                                FROM information_schema.tables
                                WHERE table_schema='public'
                                AND table_type='BASE TABLE'""")
        return [row[0] for row in rows]

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
                    # print(query, args)
                    cursor.execute(query, *args)
                elif kwargs and not args:
                    # print(query, kwargs)
                    cursor.execute(query, kwargs)
                elif not (args or kwargs):
                    # print(query)
                    cursor.execute(query)
                else:
                    raise TypeError("function takes at most 2 arguments")
                try:
                    return cursor.fetchall()
                except dbapi2.ProgrammingError:
                    pass


class DBClient:
    _TABLE_NAMES = []

    def __init__(self, database_url):
        self.database_url = database_url
        with DBHelper(database_url) as connection:
            self._TABLE_NAMES.extend(connection.get_table_names())

    def check_if_valid_item(table_names, argument_order=1):
        def decorator(function):
            wraps(function)

            def wrapper(o, *args, **kwargs):
                item = args[argument_order - 1]
                is_type = isinstance(item, type)
                class_name = item.__name__ if is_type else type(item).__name__
                if class_name.lower() in table_names:
                    return function(o, *args, **kwargs)
                else:
                    raise TypeError(f"item is not valid type: {class_name}")

            return wrapper

        return decorator

    @check_if_valid_item(_TABLE_NAMES)
    def add_item(self, item):
        _table_name = type(item).__name__
        with DBHelper(self.database_url) as connection:
            connection.insert_values(_table_name, **item.__dict__)

    def add_items(self, *iterable):
        for item in iterable:
            self.add_item(item)

    @check_if_valid_item(_TABLE_NAMES)
    def update_items(self, new_item, **conditions):
        _table_name = type(new_item).__name__
        with DBHelper(self.database_url) as connection:
            print(new_item.__dict__)
            for key, value in new_item.__dict__.items():
                connection.update_value(_table_name, key, value, **conditions)

    @check_if_valid_item(_TABLE_NAMES)
    def delete_items(self, item_type_, **conditions):
        _table_name = item_type_.__name__
        with DBHelper(self.database_url) as connection:
            connection.delete_rows(_table_name, **conditions)

    @check_if_valid_item(_TABLE_NAMES)
    def get_items(self, item_type_, columns=("*",), **conditions):
        _table_name = item_type_.__name__
        with DBHelper(self.database_url) as connection:
            return connection.select(_table_name, columns, **conditions)


if __name__ == '__main__':
    m1 = Movie(title="the usual suspects", budget=34223)
    m2 = Movie(title="fast and furious", duration=120)
    g = Genre("comedy")

    db = DBClient("postgres://postgres:docker@localhost:5432/postgres")
    db.add_items(m1, m2, g)
    db.delete_items(Movie, title="the usual suspects")
    print(db.get_items(Genre, columns=("name",)))
    print(db.get_items(Movie, columns=("title", "duration")))
