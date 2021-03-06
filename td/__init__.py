"""Simple python web app using Pyramid framework for the td project.

.. moduleauthor:: Mykola Radionov <moodaq@gmail.com>

"""

import logging
import pymongo

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

    mongo_creds = parser.get_subsection_in_section("mongo", "databases")
    client = pymongo.MongoClient(mongo_creds['host'],
                                 int(mongo_creds['port']))
    mongo_db = client[mongo_creds["db_name"]]

    db = Connector(db_engine_type_in_use, db_creds)

    def connect_db_to_view(view_to_wrap):
        """Serve as decorator specified in config.add_view for db connections
        creation.

        Inserts Connector's instance and Mongodb Database instance in
        request.registry.settings.db

        :param view_to_wrap: View func to extend.
        :return: Wrapped view func with injected db instances in it's request.
        """
        def wrapper(context, request):
            request.registry.settings["db"] = db
            request.registry.settings["mongo_db"] = mongo_db
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

    authn_policy = AuthTktAuthenticationPolicy(secret=settings["auth.secret"],
                                               callback=group_finder)

    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings, root_factory=RootFactory)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.add_static_view(name="static",
                           path="td:static",
                           cache_max_age=3600)
    config.add_forbidden_view(view="td.views.forbidden_view")

    config.add_view(view="td.views.home",
                    route_name="home",
                    permission="entry")
    config.add_view(view="td.views.get_todo_list_page",
                    route_name="todo_list",
                    request_method="GET",
                    permission="entry")
    config.add_view(view="td.views.get_todo_list_items",
                    route_name="get_todo_list_items",
                    renderer="json",
                    xhr=True,
                    request_method="GET",
                    decorator=connect_db_to_view,
                    permission="entry")
    config.add_view(view="td.views.add_todo_list_item",
                    route_name="add_todo_list_item",
                    xhr=True,
                    request_method="POST",
                    decorator=connect_db_to_view,
                    permission="entry")
    config.add_view(view="td.views.get_login_page",
                    route_name="login",
                    request_method="GET")
    config.add_view(view="td.views.post_login_credentials",
                    route_name="post_login_credentials",
                    xhr=True,
                    request_method="POST",
                    decorator=connect_db_to_view)
    config.add_view(view="td.views.logout",
                    route_name="logout")
    config.add_view(view="td.views.remove_item",
                    route_name="remove_item")

    config.add_route(name="home", path="/")
    config.add_route(name="todo_list", path="/todo_list")
    config.add_route(name="get_todo_list_items",
                     path="/api/get_todo_list_items")
    config.add_route(name="add_todo_list_item", path="/api/add_todo_list_item")
    config.add_route(name="login", path="/login")
    config.add_route(name="post_login_credentials",
                     path="/api/post_login_credentials")
    config.add_route(name="logout", path="/logout")
    config.add_route(name="remove_item", path="/api/remove_item")

    return config.make_wsgi_app()
