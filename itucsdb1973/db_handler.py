import psycopg2 as dbapi2
from functools import wraps
from itucsdb1973.data_model import Movie


class NotUniqueError(Exception):
    pass


class DBHelper:
    def __init__(self, database_url):
        self.__db_url = database_url
        self.__conn = dbapi2.connect(database_url)
        self.__c = self.__conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def create_table(self, table_name, column_spec):
        query = f"CREATE TABLE IF NOT EXISTS {table_name} " \
                f"({', '.join(column_spec)})"
        self._execute(query)

    def insert_values(self, table_name, returning=("id",), **kwargs):
        query = f"INSERT INTO {table_name} ({', '.join(kwargs.keys())}) " \
                f"VALUES ({', '.join('%s' for _ in kwargs)})" + \
                self.get_returning_clause(returning)
        return self._execute(query, list(kwargs.values()))

    @staticmethod
    def get_returning_clause(returning):
        if returning:
            return f" returning {', '.join(returning)}"
        return ""

    def delete_rows(self, table_name, returning=("id",), **conditions):
        query = f"DELETE FROM {table_name} " + \
                self.get_where_clause(conditions) + \
                self.get_returning_clause(returning)

        return self._execute(query)

    def update_value(self, table_name, key, new_value,
                     returning=("id",), **conditions):
        query = f"UPDATE {table_name} SET {key} = '{new_value}'" + \
                self.get_where_clause(conditions) + \
                self.get_returning_clause(returning)
        return self._execute(query)

    def select(self, table_name_, columns, on_conditions=None,
               group_by=None, order_by=None, limit=None,
               offset=None, like=None,
               **conditions):
        if on_conditions:
            num_of_tables = len(table_name_.split(" join "))
            if num_of_tables != 2:
                raise Exception("this join operation is not valid")
        query = f"SELECT {', '.join(columns)} FROM {table_name_}" + \
                self.get_clause("ON", on_conditions) + \
                self.get_where_clause(conditions, like) + \
                self.get_clause("GROUP BY", group_by) + \
                self.get_clause("ORDER BY", order_by) + \
                self.get_clause("LIMIT", limit) + \
                self.get_clause("OFFSET", offset)

        return self._execute(query)

    @staticmethod
    def get_clause(keyword, params):
        if params:
            return f" \n{keyword} {params} "
        return ""

    def drop_table(self, table_name, delete_option=""):
        self._execute(f"DROP TABLE IF EXISTS {table_name} {delete_option}")

    def get_table_names(self):
        rows = self.select("information_schema.tables",
                           columns=("table_name",),
                           table_schema='public', table_type='BASE TABLE')
        return [row[0] for row in rows]

    def get_column_names(self, table_name):
        rows = self.select("information_schema.columns",
                           columns=("column_name",),
                           table_name=table_name)
        return [row[0] for row in rows]

    def commit(self):
        self.__conn.commit()

    def close(self):
        self.__conn.close()

    @staticmethod
    def get_where_clause(conditions, like=""):
        if conditions:
            q = "\nWHERE "
            q += " AND ".join(
                f"{key} = {repr(conditions[key])}" for key in conditions)
            if like:
                q += f" AND {like} "
            return q
        elif like:
            return f"\nWHERE {like}"
        else:
            return ""

    def _execute(self, query, *args, **kwargs):
        with dbapi2.connect(self.__db_url) as conn:
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


class DBClient(DBHelper):
    _TABLE_NAMES = []

    def __init__(self, database_url, check_tables=True):
        super().__init__(database_url)
        self.database_url = database_url
        if check_tables:
            self.check_tables()

    def check_tables(self):
        self._TABLE_NAMES.extend(self.get_table_names())

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
    def add_item(self, item, returning=("id",), check_if_exists=False):
        table_name_ = type(item).__name__
        if table_name_ == "UserM":
            del item.active
        if check_if_exists:
            items = self.get_items(item, returning, **item.__dict__)
            if items:
                return items
        try:
            return self.insert_values(table_name_, returning=returning,
                                      **item.__dict__)
        except dbapi2.errors.UniqueViolation as e:
            print("hey")
            raise NotUniqueError(e)

    def add_items(self, *iterable):
        for item in iterable:
            self.add_item(item)

    @check_if_valid_item(_TABLE_NAMES)
    def update_items(self, new_item, **conditions):
        table_name_ = type(new_item).__name__
        for key, value in new_item.__dict__.items():
            self.update_value(table_name_, key, value, **conditions)

    @check_if_valid_item(_TABLE_NAMES)
    def delete_items(self, item_type_, returning=("id",), **conditions):
        table_name_ = item_type_.__name__
        self.delete_rows(table_name_, returning=returning, **conditions)

    @check_if_valid_item(_TABLE_NAMES)
    def get_items(self, item_type_, columns=("*",), primary_key=("id",),
                  **conditions):
        if not isinstance(item_type_, type):
            item_type_ = type(item_type_)
        table_name_ = item_type_.__name__.lower()
        with DBHelper(self.database_url) as connection:
            all_columns = connection.get_column_names(table_name_)
            if not set(primary_key).issubset(set(all_columns)):
                message = f"{repr(primary_key)} is not found in {table_name_}"
                raise KeyError(message)
            if columns in [("*",), "*"]:
                columns = all_columns

            non_key_columns = tuple(set(columns).difference(set(primary_key)))
            columns = primary_key + non_key_columns
            data = connection.select(table_name_, columns, **conditions)
        result = []
        for datum in data:
            item = item_type_.from_sql_data(columns, datum)
            result.append((datum[0:len(primary_key)], item))
        return result

    @check_if_valid_item(_TABLE_NAMES)
    def get_item(self, item_type_, columns=("*",), primary_key=("id",),
                 **conditions):
        items = self.get_items(item_type_, columns, primary_key,
                               **conditions)
        try:
            return items[0]
        except IndexError:
            return None, None


if __name__ == '__main__':
    m1 = Movie(title="the usual suspects", budget=34223, vote_average=3.5)
    m2 = Movie(title="fast and furious", duration=120, budget=30,
               vote_average=5.0)
    # g = Genre("comedy")
    db = DBClient("postgres://postgres:docker@localhost:5432/postgres")
    db.add_items(m1, m2)
    db.update_items(Movie(title="asdfg"), title="fast and furious")
    # db.delete_items(Movie, title="the usual suspects")
    # genres = db.get_items(Genre, columns=("name",))
    # movies = db.get_items(Movie, columns=("title", "duration"))
    # print(genres)
    # print(movies)
    for item in db.select("movie_genre join genre", ("name", "count(name)"),
                          on_conditions="genre_id=id",
                          group_by="name",
                          order_by="count desc", limit=10, offset=0,
                          name="Mystery"
                          ):
        print(item)
    # countries = db.get_items(Movie, columns=("*"))
    # print(countries)
