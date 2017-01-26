"""
.. module:: views
   :platform: Unix
   :synopsis: Context-manager wrapper for MySQLdb connection.

.. moduleauthor:: Mykola Radionov <moodaq@gmail.com>


"""


import MySQLdb


class DbAssessor(object):
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
        like DbAssesor_instance.cursor.execute(<raw_sql>) or
        DbAssessor_instance.cursor.fetchall().

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
