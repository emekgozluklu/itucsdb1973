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
    person = db.get_items(Person, first_name="John")[0]

Updating items in database
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To update an item, you need to pass your new item to the DBClient's
update_items method:

.. code-block:: python

    db = DBClient("DB_URL")
    person = db.get_items(Person, first_name="John")[0]
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

