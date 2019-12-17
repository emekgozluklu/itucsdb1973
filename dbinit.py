import os
import sys

import psycopg2 as dbapi2

INIT_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS MOVIE (
            ID SERIAL PRIMARY KEY,
            BUDGET BIGINT,
            IMDB_ID VARCHAR(12),
            LANGUAGE VARCHAR(2),
            OVERVIEW TEXT,
            RELEASE_DATE DATE,
            DURATION INTEGER,
            TITLE TEXT,
            VOTE_AVERAGE NUMERIC,
            VOTE_COUNT INTEGER)""",
    """CREATE TABLE IF NOT EXISTS GENRE (
            ID SERIAL PRIMARY KEY,
            NAME TEXT)""",
    """CREATE TABLE IF NOT EXISTS MOVIE_GENRE(
            MOVIE_ID INTEGER REFERENCES MOVIE (ID) ON DELETE CASCADE,
            GENRE_ID INTEGER  REFERENCES GENRE (ID) ON DELETE CASCADE,
            PRIMARY KEY (MOVIE_ID, GENRE_ID)
    )""",
    """CREATE TABLE IF NOT EXISTS USERM(
            ID TEXT PRIMARY KEY,
            PASSWORD TEXT,
            EMAIL TEXT UNIQUE,
            JOINED_AT DATE DEFAULT CURRENT_DATE,
            PROFILE_PHOTO TEXT,
            IS_ADMIN BOOL DEFAULT FALSE,
            BIO TEXT DEFAULT ''
    )""",
    """CREATE TABLE IF NOT EXISTS COMMENT(
            ID SERIAL PRIMARY KEY,
            OWNER_ID TEXT REFERENCES USERM(ID) ON DELETE CASCADE,
            MOVIE_ID INT REFERENCES MOVIE(ID) ON DELETE CASCADE,
            CONTENT TEXT DEFAULT '',
            TIME timestamp DEFAULT NOW(),
            LIKES INT DEFAULT 0,
            DISLIKES INT DEFAULT 0,
            IS_PINNED BOOL DEFAULT FALSE
    )"""

    ]


def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        cursor.close()


def deinit(url):
    table_names = ["movie", "genre", "movie_genre", "comment"]
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for table_name in table_names:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
        cursor.close()


if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py", file=sys.stderr)
        sys.exit(1)
    deinit(url)
    initialize(url)
