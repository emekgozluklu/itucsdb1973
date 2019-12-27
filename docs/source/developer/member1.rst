Parts Implemented by Şahin Akkaya
=================================

DBCLient
--------
In order to handle database operations easily, a class named DBClient is
implemented. It inherits from DBHelper which includes necessary methods
for reading, writing, updating and deleting operations and defines new
methods for making this operations easy.

Adding items to database
~~~~~~~~~~~~~~~~~~~~~~~~
Let's say that you created a class named Person which takes first name,
last name and age:

.. code-block:: python

    class Person:
            def __init__(self, first_name, last_name, age):
                self.f_name = first_name
                self.l_name = last_name
                self.age = age


Then you created a Person object and you want to store this object in
database using DBClient. All you need to do is create a table which
takes its name from your class and takes it columns from the attributes
of your class. You can also use DBHelper class to create this table:

.. code-block:: python
    class DBHelper:
        ...
        def create_table(self, table_name, column_spec):
            query = f"CREATE TABLE IF NOT EXISTS {table_name} " \
                    f"({', '.join(column_spec)})"
            self._execute(query)
        ...

    db = DBHelper("DB_URL")
    db.create_table("PERSON", ("f_name", "l_name", "age"))

After this your table is created if it's not already exists but it
does not have any restriction on its columns so you may want to create
it manually:


.. code-block:: sql

    CREATE TABLE IF NOT EXISTS (
        ID SERIAL PRIMARY KEY,
        F_NAME VARCHAR(100),
        L_NAME VARCHAR(100),
        AGE INTEGER,
    )

Now you can add your person object to the database with this:
.. code-block:: python
    person = Person("Şahin", "Akkaya", 20)
    db = DBClient("DB_URL")
    db.add_item(person)





