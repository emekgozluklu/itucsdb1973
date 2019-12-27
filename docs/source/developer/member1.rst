Parts Implemented by Şahin Akkaya
=================================

DBCLient
--------
In order to handle database operations easily, a class named DBClient is
implemented. It inherits from DBHelper which includes necessary methods
for reading, writing, updating and deleting operations and defines new
methods for making these operations easy.

Adding items to database
~~~~~~~~~~~~~~~~~~~~~~~~
Let's say that you created a class named Person which takes first name and
last name then creates a simple email address from these:

.. code-block:: python

    class Person:
            def __init__(self, first_name, last_name):
                self.first_name = first_name
                self.last_name = last_name
                self.email = first_name + last_name + "@example.domain"


Then you created a Person object and you want to store this object in
database using DBClient. All you need to do is create a table which
takes its name from your class and takes it columns from the attributes
of your class.

.. code-block:: sql

    CREATE TABLE IF NOT EXISTS (
        ID SERIAL PRIMARY KEY,
        FIRST_NAME VARCHAR(20),
        LAST_NAME VARCHAR(20),
        EMAIL VARCHAR(50)
    )

Now you can add your person object to the database with this:

.. code-block:: python

    class DBClient(DBHelper):
        @check_if_valid_item(_TABLE_NAMES)
        def add_item(self, item, returning=("id",), check_if_exists=False):
            table_name_ = type(item).__name__
            ...
            if check_if_exists:
                items = self.get_items(item, returning, **item.__dict__)
                if items:
                    return items
            try:
                return self.insert_values(table_name_, returning=returning,
                                          **item.__dict__)
            except dbapi2.errors.UniqueViolation as e:
                raise NotUniqueError(e)

    person = Person("sahin", "akkaya")
    db = DBClient("DB_URL")
    db.add_item(person)

Before running this method, a decorator is applied which checks if there
is a table with given object's class and if there is not an exception is
raised. In our case, we created table "Person" in our database so we can
continue. Basically, this method passes all the attributes of your object
to DBHelper's insert_values method as a dict. Then required sql query is
generated and executed. If you want to return some other thing, you can
specify it.

.. code-block:: python

    name, email = db.add_item(person, returning=("first_name", "email"))[0]
    print(name) # 'sahin'
    print(email) # 'sahinakkaya@example.domain'

And you can also make sure you are not adding duplicate of some data by
setting check_if_exists parameter to True:

.. code-block:: python

    id_ = db.add_item(person, check_if_exists=True)[0]
    print(id_) # 1
    id_ = db.add_item(person, check_if_exists=True)[0]
    print(id_) # 1
    person = Person("John", "Doe")
    id_ = db.add_item(person, check_if_exists=True)[0]
    print(id_) # 2

Getting items from database
~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can get the items with DBClient's get_items method:

.. code-block:: python

    db = DBClient("DB_URL")
    id_, person = db.get_items(Person, first_name="John")[0]
    print(person.email) # JohnDoe@example.domain

Updating items in database
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To update an item, you need to pass your new item to the DBClient's
update_items method:

.. code-block:: python

    db = DBClient("DB_URL")
    id_, person = db.get_items(Person, first_name="John")[0]
    person.first_name = "Jane"
    db.update_items(person, first_name="John")
    # All the persons whose name is John are updated with new name, Jane.

Deleting items from database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To delete an item you need to pass the class that item belongs to and
deleting conditions if you want:

.. code-block:: python

    db = DBClient("DB_URL")
    db.delete_items(Person, name="sahin")
    # All the persons whose name is sahin are deleted.


The Actual Tables
-----------------
Once we introduced the DBClient, performing database operations is really
easy. Most of the time there is no need to write SQL statements manually. It's only
required while creating tables, to specify column types, and one or two
exceptional cases.


1. Movie
~~~~~~~~

a. Creating
~~~~~~~~~
The following SQL query is used to create MOVIE table:

.. code-block:: sql

    CREATE TABLE IF NOT EXISTS MOVIE (
            ID SERIAL PRIMARY KEY,
            BUDGET BIGINT,
            IMDB_ID VARCHAR(12),
            LANGUAGE VARCHAR(2),
            OVERVIEW TEXT,
            RELEASE_DATE DATE,
            DURATION INTEGER,
            TITLE TEXT,
            VOTE_AVERAGE NUMERIC,
            VOTE_COUNT INTEGER)

b. Adding
~~~~~~~~~

Here is the related part of code for adding a Movie to the database in flask
application:

.. code-block:: python

    def add_movie():
        ...
        movie = data_model.Movie(False, **request.form) # movie is created from form data
        movie_id = db.add_item(movie)[0][0] # <-- just one line and the movie is added
        ...


Adding a new movie will also require new items to be inserted into MOVIE_GENRE
table which holds the genres of movies. Since a movie could have more than one
genre, this value should be stored in separate table, i.e. MOVIE_GENRE.

.. code-block:: python

    genre_ids = request.form.getlist("genres")
    for genre_id in genre_ids:
        db.insert_values("movie_genre", movie_id=movie_id,
                         genre_id=genre_id, returning="")

c. Updating
~~~~~~~~~~~
Update operation for movie is handled in ``movie`` function which takes
``movie_id`` as parameter. Necessary bits of code is listed below:

.. code-block:: python

    def movie(movie_id):
        ...
        movie = data_model.Movie(False, **request.form)
        movie_id = db.update_items(movie, id=movie_id)[0][0]
        genre_ids = request.form.get("genres")
        db.delete_rows("movie_genre", returning="", movie_id=movie_id)
        for genre_id in genre_ids:
            db.insert_values("movie_genre", movie_id=movie_id,
                             genre_id=genre_id, returning="")

d. Deleting
~~~~~~~~~~~


Required piece of code for deleting a movie is listed below. The ``movie_key`` is
just a field in the form which holds the ``movie_id`` as a value:

.. code-block:: python

    movie_key = request.form.get("movie_key")
    db.delete_items(data_model.Movie, id=movie_key)

.. warning:: Deleting a movie will also delete all the comments made to that movie. See the creation of comments_.


2. User
~~~~~~~

a. Creating
~~~~~~~~~~~

The following SQL query is used to create USERM table which will store the users
in the application:

.. code-block:: sql

    CREATE TABLE IF NOT EXISTS USERM(
            ID TEXT PRIMARY KEY,
            PASSWORD TEXT,
            EMAIL TEXT UNIQUE,
            JOINED_AT DATE DEFAULT CURRENT_DATE,
            PROFILE_PHOTO TEXT,
            IS_ADMIN BOOL DEFAULT FALSE,
            BIO TEXT DEFAULT ''
    )

.. note:: The name "USERM" is chosen because "USER" was conflicting with PostgreSQL's keywords.

b. Adding
~~~~~~~~~

Here is the related part of code for adding a user to the database in flask
application:

.. code-block:: python

    def signup():
        ...
        password = hasher.hash(form.password.data)
        user = data_model.UserM(form.username.data, password,
                                form.email.data, form.profile_photo.data)
        try:
            db.add_item(user)
        except NotUniqueError as e:
            if f"Key (id)=({form.username.data})" in str(e):
                form.username.errors.append("username already in use")
            else:
                form.email.errors.append("email address already in use")
        else:
            return redirect(url_for('login'))
        return render_template('signup_page.html', form=form)


The password is hashed before creating the UserM object to provide more security.
Then the newly created user is added to database if no exception occurs.
Exceptional cases occurs when username or email address is already in use and
are handled properly to give user information about the situation.

c. Updating
~~~~~~~~~~~
Update operation for user is limited with just two fields, email or bio.
Necessary bits of code is listed below:

.. code-block:: python

    def edit_profile():
        ...
        user = get_user(current_user.id)
        user.bio = form.data["bio"]
        user.email = form.data["email"]
        try:
            db.update_items(user, id=current_user.id)
        except NotUniqueError:
            form.email.errors.append("email address already in use")
        ...

As in register operation, user may choose an email which violates uniqueness
constraint on ``email`` column so required checks are included and user is
informed.

d. Deleting
~~~~~~~~~~~
It's best to delete a user by specifying the id. This will ensure that only one
and correct user is deleted. The necessary code for delete operation is listed
below:

.. code-block:: python

    def delete_profile():
        ...
        id = current_user.id
        logout_user()
        db.delete_items(data_model.UserM, id=id))

.. warning:: Deleting a user will also delete all the comments of that user. See the creation of comments_.

.. _comments:
3. Comment
~~~~~~~
a. Creating
~~~~~~~~~~~

The following SQL query is used to create COMMENT table which will store the
comments made by users to movies in the application:

.. code-block:: sql

    CREATE TABLE IF NOT EXISTS COMMENT(
            ID SERIAL PRIMARY KEY,
            OWNER_ID TEXT REFERENCES USERM(ID) ON DELETE CASCADE,
            MOVIE_ID INT REFERENCES MOVIE(ID) ON DELETE CASCADE,
            CONTENT TEXT DEFAULT '',
            TIME timestamp DEFAULT NOW(),
            LIKES INT DEFAULT 0,
            DISLIKES INT DEFAULT 0,
            IS_PINNED BOOL DEFAULT FALSE
    )

As it can be seen from above, OWNER_ID and MOVIE_ID are foreign keys which
references the ID columns of USERM and MOVIE table respectively.

.. note:: Since OWNER_ID is foreign key for user, in order to perform an operation related with comment (i.e. add comment, delete comment etc.) user must be logged in.

b. Adding
~~~~~~~~~

Here is the related part of code for adding a comment for a movie in the
application:


.. code-block:: python

    def add_comment(movie_id):
        ...
        content = request.form.get("content")
        comment = data_model.Comment(current_user.id, movie_id, content)
        db.add_item(comment)
        ...


Since some attributes of a comment can take default value, such as number of
likes and dislikes are initially 0 or comment time is equal to current time,
they are not considered while creating the comment object.

c. Updating
~~~~~~~~~~~
Update operation for a comment is limited with just pinning or unpinning
comments. Necessary bits of code is listed below:

.. code-block:: python

    def toggle_pin(movie_id):
        ...
        comment_id = request.form.get("comment_id")
        _, comment = db.get_item(data_model.Comment, id=comment_id)
        comment.is_pinned = not comment.is_pinned
        db.update_items(comment, id=comment_id)


d. Deleting
~~~~~~~~~~~
Like in the previous data models, in order to delete something, simply calling
``delete_items`` method of ``DBClient`` is sufficient.

.. code-block:: python

    def delete_comment():
        ...
        comment_id = request.form.get("comment_id")
        db.delete_items(data_model.Comment, id=comment_id)
        ...

.. warning:: Deleting a movie will also delete all the comments made to that movie.
.. warning:: Deleting a user will also delete all the comments of that user.





