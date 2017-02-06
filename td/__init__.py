"""Simple python web app using Pyramid framework for the td project.

.. moduleauthor:: Mykola Radionov <moodaq@gmail.com>

"""

from ConfigParser import SafeConfigParser
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory

from td.config import ConfigScanner
from td.assessors.assessors import Connector

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    parser = SafeConfigParser()
    parser.read(global_config['__file__'])
    for k, v in parser.items('databases'):
        settings[k] = v


    parser = ConfigScanner(global_config['__file__'])
    pgres_creds = parser.get_subsection_in_section('postgres', 'databases')
    #db = Connector('postgres')

    config = Configurator(settings=settings)

    config.add_static_view("static",
                           path="td:static",
                           cache_max_age=3600)

    config.add_view('td.views.home', route_name='home')
    config.add_view('td.views.get_todo_list_page',
                    route_name='todo_list',
                    request_method="GET",
                    view_options='test')
    config.add_view('td.views.get_todo_list_items',
                    route_name='get_todo_list_items',
                    renderer="json",
                    request_method="GET")
    config.add_view('td.views.add_todo_list_item',
                    route_name='add_todo_list_item',
                    request_method="POST")

    config.add_route("home", "/")
    config.add_route("todo_list", "/todo_list")
    config.add_route("get_todo_list_items", "/api/get_todo_list_items")
    config.add_route("add_todo_list_item", "/api/add_todo_list_item")

    my_session_factory = SignedCookieSessionFactory("super_secret")
    config.set_session_factory(my_session_factory)

    config.scan()
    return config.make_wsgi_app()
