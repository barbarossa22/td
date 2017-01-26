"""
.. module:: views
   :platform: Unix
   :synopsis: Context-manager wrapper for MySQLdb connection.

.. moduleauthor:: Mykola Radionov <moodaq@gmail.com>


"""


import MySQLdb
import psycopg2


class MySQLDbAssessor():
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


class PgresDbAssessor():
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
        self.db = psycopg2.connect(dbname = self.dbname,
                                   user = self.user,
                                   host = self.host,
                                   password = self.password)
        return self.db

    def __exit__(self, *args):
        """Exit the context and perform cleanup closing db connection."""
        self.db.close()

