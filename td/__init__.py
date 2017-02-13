"""Simple python web app using Pyramid framework for the td project.

.. moduleauthor:: Mykola Radionov <moodaq@gmail.com>

"""

import logging

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.security import Allow, Everyone

from td.assessors.assessors import Connector
from td.config import ConfigScanner

logger = logging.getLogger(__name__)


class RootFactory(object):
    """List of mappings from principal to permission."""
    def __init__(self, request):
        pass

    def __acl__(self):
        """Return list of mappings from principal to permission."""
        return [(Allow, Everyone, "everybody"),
                (Allow, "group:users", "entry")]


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    parser = ConfigScanner(global_config["__file__"])

    db_engine_type_in_use = settings["db_in_use"]
    db_creds = parser.get_subsection_in_section(db_engine_type_in_use, "databases")

    settings["mongo_creds"] = parser.get_subsection_in_section("mongo",
                                                               "databases")

    db = Connector(db_engine_type_in_use, db_creds)

    def connect_db_to_view(view_to_wrap):
        """Serve as decorator specified in config.add_view for db connections
        creation.

        Inserts Connector's instance in request.registry.settings.db.

        :param view_to_wrap: View func to extend.
        :return: Wrapped view func with injected db instance in it's request.
        """
        def wrapper(context, request):
            request.registry.settings["db"] = db
            response = view_to_wrap(context, request)
            return response
        return wrapper

    def group_finder(userid, request):
        """Find all groups of user in the database and return list of them.

        :param userid: user's login name.
        :type userid: str
        :param request: instance-object which represents HTTP request.
        :type request: pyramid.request.Request
        :return: list of groups (empty if no groups at all).
        :rtype: list
        """
        query_output = db.select_one("groups", "Users",
                                     "username='%s'" % userid)
        if query_output is not None:
            groups_list = query_output[0].split(", ")
            logger.debug("Authenticated user in this request is in groups: %s",
                         groups_list)
            return groups_list
        return []

    authn_policy = AuthTktAuthenticationPolicy(settings["auth.secret"],
                                               callback=group_finder)

    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings, root_factory=RootFactory)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.add_static_view("static",
                           path="td:static",
                           cache_max_age=3600)
    config.add_forbidden_view("td.views.forbidden_view")

    config.add_view("td.views.home", route_name="home", permission="entry")
    config.add_view("td.views.get_todo_list_page",
                    route_name="todo_list",
                    request_method="GET",
                    permission="entry")
    config.add_view("td.views.get_todo_list_items",
                    route_name="get_todo_list_items",
                    renderer="json",
                    xhr=True,
                    request_method="GET",
                    decorator=connect_db_to_view,
                    permission="entry")
    config.add_view("td.views.add_todo_list_item",
                    route_name="add_todo_list_item",
                    xhr=True,
                    request_method="POST",
                    decorator=connect_db_to_view,
                    permission="entry")
    config.add_view("td.views.get_login_page",
                    route_name="login",
                    request_method="GET")
    config.add_view("td.views.post_login_credentials",
                    route_name="post_login_credentials",
                    xhr=True,
                    request_method="POST",
                    decorator=connect_db_to_view)
    config.add_view("td.views.logout",
                    route_name="logout")

    config.add_route("home", "/")
    config.add_route("todo_list", "/todo_list")
    config.add_route("get_todo_list_items", "/api/get_todo_list_items")
    config.add_route("add_todo_list_item", "/api/add_todo_list_item")
    config.add_route("login", "/login")
    config.add_route("post_login_credentials", "/api/post_login_credentials")
    config.add_route("logout", "/logout")

    return config.make_wsgi_app()
