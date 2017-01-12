"""Simple python web app using Pyramid framework for the td project.

.. moduleauthor:: Mykola Radionov <moodaq@gmail.com>

"""

from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    config.add_static_view('static', path='/home/mrad/td/td/static',
                            cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('todo_list', '/todo_list')
    config.add_route('get_todo_list_items', '/api/get_todo_list_items')
    config.add_route('add_todo_list_item', '/api/add_todo_list_item')

    my_session_factory = SignedCookieSessionFactory('super_secret')
    config.set_session_factory(my_session_factory)

    config.scan()
    return config.make_wsgi_app()
