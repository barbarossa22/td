"""
.. module:: assessors
   :platform: Unix
   :synopsis: Database assessors.

.. moduleauthor:: Mykola Radionov <moodaq@gmail.com>


"""


import MySQLdb
import psycopg2

from pyramid.threadlocal import get_current_registry

from td.exceptions import WrongEngineException


class MySQLDbAssessor:
    """Context-manager for MySQLdb connection to the database.

    """
    def __init__(self, host, user, password, db_name):
        """Initialize context-manager call with credentials.

        :param host: hostname.
        :type: str
        :param user: username for authentication to local MySQL db server.
        :type: str
        :param password: password for authentication to local MySQL db server.
        :type: str
        :param db_name: database name to use.
        :type: str

        """
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name

    def __enter__(self):
        """Return the resource of db connection to be managed in a context.

        Also assigns to created instance cursor object so it can be used later
        like MySQLDbAssesor_instance.cursor.execute(<raw_sql>) or
        MySQLDbAssessor_instance.cursor.fetchall().

        :return: MySQLdb connection object.
        """
        self.db = MySQLdb.connect(self.host,
                                  self.user,
                                  self.password,
                                  self.db_name)
        self.db.cursor = self.db.cursor()
        return self.db

    def __exit__(self, *args):
        """Exit the context and perform cleanup closing db connection."""
        self.db.close()


class PgresDbAssessor:
    """Context-manager for psycopg2 connection to the database.

    """
    def __init__(self, dbname, user, host, password):
        """Initialize context-manager call with credentials.

        :param dbname: database name to use.
        :type: str
        :param user: username for authentication to local Postgres db server.
        :type: str
        :param host: hostname.
        :type: str
        :param password: password for authentication to local Postgres server.
        :type: str

        """
        self.dbname = dbname
        self.user = user
        self.host = host
        self.password = password

    def __enter__(self):
        """Return the resource of db connection to be managed in a context.

        :return: psycopg2 connection object.
        """
        self.db = psycopg2.connect(dbname=self.dbname,
                                   user=self.user,
                                   host=self.host,
                                   password=self.password)
        return self.db

    def __exit__(self, *args):
        """Exit the context and perform cleanup closing db connection."""
        self.db.close()


class Connector(object):
    """Connector to mysql or postgres databases with interface for select
    queries.

    Initialize class passing to it engine_type string ('mysql' or 'postgres').
    On initialization selected database credentials are retrieved from td app
    registry settings which were parsed previously from the current working
    config file. Two public methods available: select_one and select_all which
    send select queries to the database server establishing connection with it
    using MySQLDbAssessor and PgresDbAssessor drivers as context managers for
    each single request.
    """

    def __init__(self, engine_type):
        """Initialize Connector with provided as arg database type. Get needed
        databases credentials and params from app's registry settings.

        :param engine_type: Type of engine ('mysql' or 'postgres').
        :type engine_type: str.
        """
        self.engine_type = engine_type
        self.ERROR_MESSAGE = ("Wrong argument describing engine type. Use "
                              "'mysql' or 'postgres'.")
        self.__credentials_dict = self.__retrieve_creds_from_cfg(
            self.engine_type
        )

    def __retrieve_creds_from_cfg(self, engine_type):
        """
        Get db credentials from 'database' section of .ini config file.

        :param engine_type: Type of engine (mysql or postgres).
        :type engine_type: str.
        :return: dictionary with db credentials and settings.
        :rtype: dict
        :raises: WrongEngineException
        """
        registry = get_current_registry()
        settings = registry.settings

        try:
            return {"dbname": settings["{}_db_name".format(engine_type)],
                    "user": settings["{}_user".format(engine_type)],
                    "host": settings["{}_host".format(engine_type)],
                    "password": settings["{}_password".format(engine_type)]}
        except KeyError:
            raise WrongEngineException(self.ERROR_MESSAGE)

    def select_one(self, column_names, table, where_clause=None):
        """
        Execute select query and return from it's output first row.

        Returns a tuple including string elements in it: ('1', 'User1'). If no
        data in the table for executed query then return value is None.

        :param column_names: column names in the table to select.
        :type column_names: str.
        :param table: table name in the db.in  t
        :type table: str.
        :param where_clause: condition for sql where clause.
        :type where_clause: str.
        :return: tuple representing single row or None if no data in db.
        :rtype: tuple
        :raises: WrongEngineException
        """
        if self.engine_type == "mysql":
            output = self.__exec_mysql_selection(column_names,
                                                 table,
                                                 where_clause,
                                                 how_many="one")
            return output
        elif self.engine_type == "postgres":
            output = self.__exec_pgres_selection(column_names,
                                                 table,
                                                 where_clause,
                                                 how_many="one")
            return output
        else:
            raise WrongEngineException(self.ERROR_MESSAGE)

    def select_all(self, column_names, table, where_clause=None):
        """
        Execute select query and return from it's output all rows.

        Output is a tuple with included tuples in it representing rows:
        (('1', 'User1'), ('2', 'User2')). If there is no data in the table for
        executed query then function returns single tuple ().

        :param column_names: column names in the table to select.
        :type column_names: str.
        :param table: table name in the db.
        :type table: str.
        :param where_clause: condition for sql where clause.
        :type where_clause: str.
        :return: tuple with all rows as included elements-tuples in it.
        :rtype: tuple
        :raises: WrongEngineException
        """
        if self.engine_type == "mysql":
            output = self.__exec_mysql_selection(column_names,
                                                 table,
                                                 where_clause,
                                                 how_many="all")
            return output
        elif self.engine_type == "postgres":
            output = self.__exec_pgres_selection(column_names,
                                                 table,
                                                 where_clause,
                                                 how_many="all")
            return output
        else:
            raise WrongEngineException(self.ERROR_MESSAGE)

    def __exec_mysql_selection(self,
                               column_names,
                               table,
                               where_clause=None,
                               how_many="all"):
        """
        Execute select query in mysql database.

        In case when how_many arg is equal to 'all' then function fetches all
        rows from select query. Output is a tuple with included tuples in it
        representing rows: (('1', 'User1'), ('2', 'User2')). If there is no
        data in the table for executed query then function returns single
        tuple ().

        For all other values of how_many arg only one first row is fetched as a
        tuple including string elements in it: ('1', 'User1'). If no data in
        the table for executed query then return value is None.

        :param column_names: column names in the table to select.
        :type column_names: str.
        :param table: table name in the db.
        :type table: str.
        :param where_clause: condition for sql where clause.
        :type where_clause: str.
        :param how_many: defines selection of only first row or all rows.
        :type how_many: str.
        :return: tuple with fetched data from selected query.
        :rtype: tuple
        """
        with MySQLDbAssessor(self.__credentials_dict["host"],
                             self.__credentials_dict["user"],
                             self.__credentials_dict["password"],
                             self.__credentials_dict["dbname"]) as db:
            cursor = db.cursor
            if where_clause is None:
                cursor.execute("SELECT %s FROM %s" % (column_names, table))
            else:
                cursor.execute("SELECT %s FROM %s WHERE %s" % (column_names,
                                                               table,
                                                               where_clause))
            if how_many == "all":
                return cursor.fetchall()
            else:
                return cursor.fetchone()

    def __exec_pgres_selection(self,
                               column_names,
                               table,
                               where_clause=None,
                               how_many="all"):
        """
        Execute select query in postgres database.

        In case when how_many arg is equal to 'all' then function fetches all
        rows from select query. Output is a tuple with included tuples in it
        representing rows: (('1', 'User1'), ('2', 'User2')). If there is no
        data in the table for executed query then function returns single
        tuple ().

        For all other values of how_many arg only one first row is fetched as a
        tuple including string elements in it: ('1', 'User1'). If no data in
        the table for executed query then return value is None.

        :param column_names: column names in the table to select.
        :type column_names: str.
        :param table: table name in the db to select from.
        :type table: str.
        :param where_clause: condition for sql where clause.
        :type where_clause: str.
        :param how_many: defines selection of only first row or all rows.
        :type how_many: str.
        :return: tuple with fetched data from selected query.
        :rtype: tuple
        """
        with PgresDbAssessor(self.__credentials_dict["dbname"],
                             self.__credentials_dict["user"],
                             self.__credentials_dict["host"],
                             self.__credentials_dict["password"]) as db:
            cursor = db.cursor()
            if where_clause is None:
                cursor.execute('SELECT %s FROM "%s"' % (column_names, table))
            else:
                cursor.execute('SELECT %s FROM "%s" WHERE %s' % (column_names,
                                                                 table,
                                                                 where_clause))
            if how_many == "all":
                return tuple(cursor.fetchall())
            else:
                return cursor.fetchone()

    def insert(self, table, column_names, values):
        """Execute insert statement into database.

        It is expected to have args in the next format:
        .insert("Users", "id, name", "1, Jonathan Swift")
        .insert("Users", "name", "Jonathan Swift")

        :param table: table name in the db for insert operation.
        :type table: str.
        :param column_names: column names in the table to affect.
        :type column_names: str.
        :param values: values to be inserted
        :type values: str.
        :return: None
        :rtype: None
        :raises: WrongEngineException
        """

        if self.engine_type == "mysql":
            self.__exec_mysql_insertion(table, column_names, values)
        elif self.engine_type == "postgres":
            self.__exec_pgres_insertion(table, column_names, values)
        else:
            raise WrongEngineException(self.ERROR_MESSAGE)

    def __exec_mysql_insertion(self, table, column_names, values):
        """Execute insert statement into mysql database.

        It is expected to have args in the next format:
        .insert("Users", "id, name", "1, Jonathan Swift")
        .insert("Users", "name", "Jonathan Swift")

        :param table: table name in the db for insert operation.
        :type table: str.
        :param column_names: column names in the table to affect.
        :type column_names: str.
        :param values: values to be inserted
        :type values: str.
        :return: None
        :rtype: None
        :raises: WrongEngineException
        """
        with MySQLDbAssessor(self.__credentials_dict["host"],
                             self.__credentials_dict["user"],
                             self.__credentials_dict["password"],
                             self.__credentials_dict["dbname"]) as db:
            cursor = db.cursor
            tupled_values = tuple(values.split(", "))
            if len(tupled_values) == 1:
                values = str(tupled_values)[:-2] + ")"
            else:
                values = str(tupled_values)
            cursor.execute("INSERT INTO %s(%s) VALUES %s" % (table,
                                                             column_names,
                                                             values))
            db.commit()

    def __exec_pgres_insertion(self, table, column_names, values):
        """Execute insert statement into postgres database.

        It is expected to have args in the next format:
        .insert("Users", "id, name", "1, Jonathan Swift")
        .insert("Users", "name", "Jonathan Swift")

        :param table: table name in the db for insert operation.
        :type table: str.
        :param column_names: column names in the table to affect.
        :type column_names: str.
        :param values: values to be inserted
        :type values: str.
        :return: None
        :rtype: None
        :raises: WrongEngineException
        """
        with PgresDbAssessor(self.__credentials_dict["dbname"],
                             self.__credentials_dict["user"],
                             self.__credentials_dict["host"],
                             self.__credentials_dict["password"]) as db:
            cursor = db.cursor()
            tupled_values = tuple(values.split(", "))
            if len(tupled_values) == 1:
                values = str(tupled_values)[:-2] + ")"
            else:
                values = str(tupled_values)
            cursor.execute('INSERT INTO "%s"(%s) VALUES %s' % (table,
                                                               column_names,
                                                               values))
            db.commit()
