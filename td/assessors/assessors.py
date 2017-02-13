"""
.. module:: assessors
   :platform: Unix
   :synopsis: Database assessors.

.. moduleauthor:: Mykola Radionov <moodaq@gmail.com>


"""


import MySQLdb
import psycopg2

from td.exceptions import WrongEngineException


class Assessor:
    """Return the resource of db connection """

    def __enter__(self):
        """Serve as a parent for future implementations of it's descendants
        with their own credentials and params. Enter method returns the
        resource of db connection to be managed in a context.

        :return: connection object.
        :raises: NotImplementedError
        """
        try:
            return self.db
        except AttributeError:
            error_message = ("You can only derive from Assesor class and then "
                             "use it's descendant as a context-manager!")
            raise NotImplementedError(error_message)

    def __exit__(self, *args):
        """Exit the context and perform cleanup closing db connection."""
        self.db.close()


class MySQLDbAssessor(Assessor):
    """Context-manager for MySQLdb connection to the database."""
    def __init__(self, host, user, password, db_name):
        """Initialize context-manager call with credentials.

        :param host: hostname.
        :type: str.
        :param user: username for authentication to local MySQL db server.
        :type: str.
        :param password: password for authentication to local MySQL db server.
        :type: str.
        :param db_name: database name to use.
        :type: str.

        """
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name

        self.db = MySQLdb.connect(self.host,
                                  self.user,
                                  self.password,
                                  self.db_name)


class PgresDbAssessor(Assessor):
    """Context-manager for psycopg2 connection to the database."""
    def __init__(self, db_name, user, host, password):
        """Initialize context-manager call with credentials.

        :param db_name: database name to use.
        :type: str.
        :param user: username for authentication to local Postgres db server.
        :type: str.
        :param host: hostname.
        :type: str.
        :param password: password for authentication to local Postgres server.
        :type: str.

        """
        self.db_name = db_name
        self.user = user
        self.host = host
        self.password = password

        self.db = psycopg2.connect(dbname=self.db_name,
                                   user=self.user,
                                   host=self.host,
                                   password=self.password)


class Connector(object):
    """Connector to mysql or postgres databases with interface for select /
    insert queries.

    Initialize class passing to it engine_type string ('mysql' or 'postgres')
    and it's credentials and params in the dict like {'host': 'localhost',
    'user': 'root', 'password': 1234, 'db_name': 'db'}.

    Three public methods available: select_one, select_all and insert which
    send queries to the database server establishing connection with it
    using MySQLDbAssessor and PgresDbAssessor drivers as context managers for
    each single request.
    """

    def __init__(self, engine_type, creds_dict):
        """Initialize Connector with provided as arg database type.

        :param engine_type: Type of engine ('mysql' or 'postgres').
        :type engine_type: str.
        :param creds_dict: Dict with creds and params.
        :type creds_dict: dict.
        """
        self.engine_type = engine_type
        self.__credentials_dict = creds_dict
        self.ERROR_MESSAGE = ("Wrong argument describing engine type. Use "
                              "'mysql' or 'postgres'.")

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
                             self.__credentials_dict["db_name"]) as db:
            cursor = db.cursor()
            args = (column_names, table)
            query_template = "SELECT %s FROM %s"

            if where_clause is not None:
                args += (where_clause,)
                query_template += " WHERE %s"

            cursor.execute(query_template % args)

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
        with PgresDbAssessor(self.__credentials_dict["db_name"],
                             self.__credentials_dict["user"],
                             self.__credentials_dict["host"],
                             self.__credentials_dict["password"]) as db:
            cursor = db.cursor()

            args = (column_names, table)
            query_template = 'SELECT %s FROM "%s"'

            if where_clause is not None:
                args += (where_clause,)
                query_template += ' WHERE %s'

            cursor.execute(query_template % args)

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
            assessor = MySQLDbAssessor
            query_template = "INSERT INTO %s(%s) VALUES %s"
        elif self.engine_type == "postgres":
            assessor = PgresDbAssessor
            query_template = 'INSERT INTO "%s"(%s) VALUES %s'
        else:
            raise WrongEngineException(self.ERROR_MESSAGE)

        with assessor(db_name=self.__credentials_dict["db_name"],
                      user=self.__credentials_dict["user"],
                      host=self.__credentials_dict["host"],
                      password=self.__credentials_dict["password"]) as db:
            cursor = db.cursor()
            tupled_values = tuple(values.split(", "))
            if len(tupled_values) == 1:
                values = str(tupled_values)[:-2] + ")"
            else:
                values = str(tupled_values)
            cursor.execute(query_template % (table,
                                             column_names,
                                             values))
            db.commit()
