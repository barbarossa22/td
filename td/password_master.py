"""
.. module:: password_master
   :platform: Unix
   :synopsis: Password hasher and checker for td app.

.. moduleauthor:: Mykola Radionov <moodaq@gmail.com>


"""
import bcrypt


class PasswordMaster(object):
    """Provide work with passwords hashing and checking."""

    def hash_password(self, password):
        """ Hash password.

        :param password: password to hash
        :type password: str.
        :return: hashed password in string
        :rtype: str.
        """
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf8"), salt)
        return hashed_password

    def check_password(self, password, hashed_password):
        """Check if args are equal and return True if yes, False if no.

        :param password: password to compare.
        :type password: str.
        :param hashed_password: hashed pword value to compare.
        :type hashed_password: str.
        :return: True or False on passwords comparison.
        :rtype: bool.
        """
        result = bcrypt.checkpw(password.encode("utf8"), hashed_password)
        return result
