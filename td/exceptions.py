"""
.. module:: exceptions
   :platform: Unix
   :synopsis: Exceptions for td app.

.. moduleauthor:: Mykola Radionov <moodaq@gmail.com>


"""

class WrongEngineException(Exception):
    """Class for exceptions which should trigger when wrong engine type is
    provided as argument to function call.
    """
    def __init__(self, message, *args):
        self.message = message
        super(WrongEngineException, self).__init__(message, *args)