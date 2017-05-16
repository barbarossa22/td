"""
.. module:: auth_views
   :platform: Unix
   :synopsis: Views for td app authentication and authorization.

.. moduleauthor:: Mykola Radionov <moodaq@gmail.com>


"""


import logging
import os

from pyramid.httpexceptions import HTTPFound, HTTPUnauthorized
from pyramid.response import FileResponse
from pyramid.security import remember, forget, authenticated_userid

from td.password_master import PasswordMaster


logger = logging.getLogger(__name__)


class AuthViews(object):
    """Authentication views.
    """

    def __init__(self, request):
        self.request = request

    def forbidden_view(self):
        """Forbidden view to be thrown when user is not authorized / don't
        have proper permission.

        :return: HTTPFound to /login location to force user authentication.
        :rtype: pyramid.httpexceptions.HTTPFound
        """
        return HTTPFound(location="/login")

    def get_login_page(self):
        """Return static/login.html at request on /login url.

        :return: object that is used to serve a file from static/login.html.
        :rtype: pyramid.response.FileResponse
        """
        logger.debug("Get request for resource at /login and replied with "
                     "file static/login.html")
        abs_path_to_html_page = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                             "static",
                                             "login.html")
        return FileResponse(path=abs_path_to_html_page, cache_max_age=3600)

    def post_login_credentials(self):
        """Accept POST request with login and password from the client.

        :return: if ok HTTPFound with auth. headers in response else
        HTTPUnauthorized.

        :rtype: pyramid.httpexceptions.HTTPFound
        """
        login = self.request.json_body["login"]
        password = self.request.json_body["password"]
        password_master = PasswordMaster()

        db = self.request.registry.settings["db"]
        query_output = db.select_one("password", "Users",
                                     "username='%s'" % login)

        if query_output is not None:
            hashed_pword_from_db = query_output[0]
            if password_master.check_password(password, hashed_pword_from_db):
                headers = remember(request=self.request, userid=login)
                logger.debug("User %s has logged in right now.", login)
                return HTTPFound(location="/todo_list", headers=headers)
            else:
                logger.debug("Wrong password.")
                return HTTPUnauthorized()
        logger.debug("No such username in db.")
        return HTTPUnauthorized()

    def logout(self):
        """Logout user.

        :return: HTTPFound exception as response object with status code 302.
        :rtype: pyramid.httpexceptions.HTTPFound
        """
        headers = forget(self.request)
        logger.debug("User %s logged out.", authenticated_userid(self.request))
        return HTTPFound(location="/login", headers=headers)
