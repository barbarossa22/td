"""
.. module:: views
   :platform: Unix
   :synopsis: Views for td app.

.. moduleauthor:: Mykola Radionov <moodaq@gmail.com>


"""


import logging
import os

from pyramid.httpexceptions import HTTPFound
from pyramid.response import FileResponse, Response
from pyramid.view import view_config


logger = logging.getLogger(__name__)


@view_config(route_name='home')
def home(request):
    """Redirect from / to /todo_list url.

    :param request: instance of pyramid.request.Request class, which is
    created and put as arg for this function by router; represents HTTP
    request.
    :type request: instance
    :returns: instance of pyramid.httpexceptions.HTTPFound exception as
    response object with status code 302.
    :raises: HTTPFound

    """
    logger.debug('''Get request for the resource at / and redirected to \
/todo_list url.''')
    return HTTPFound(location='/todo_list')


@view_config(route_name='todo_list', request_method='GET')
def get_todo_list_page(request):
    """Return static/base.html at request on /todo_list url.

    :param request: instance of pyramid.request.Request class, which is
    created and put as arg for this function by router; represents HTTP
    request.
    :type request: instance
    :returns: a FileResponse object that is used to serve a static file from
    location static/base.html.

    """
    logger.debug('''Get request for resource at /todo_list and replied with \
file static/base.html''')
    abs_path_to_base = os.getcwd() + '/td/static/base.html'
    return FileResponse(abs_path_to_base, cache_max_age=3600)


@view_config(
    route_name='get_todo_list_items',
    renderer='json',
    request_method='GET'
)
def get_todo_list_items(request):
    """Get JSON with list of todo-items from session memory at request on
    /api/get_todo_list_items url.

    :param request: instance of pyramid.request.Request class, which is
    created and put as arg for this function by router; represents HTTP
    request.
    :type request: instance
    :returns: response object with included JSON-serialized string:
    * {'items': ['sleep', 'eat', 'repeat']} if in session memory there are
    items like 'sleep', 'eat', 'repeat' or some other user-defined notes.
    * {'items': null} otherwise, if 'items' list doesn't exist.

    """
    session = request.session
    logger.debug('Get request for todo list items at /api/get_todo_list_items')
    if session.get('items'):
        logger.debug('''Found existing items in session memory, reply with \
{'items': %s} JSON object.''' % session['items'])
        return {'items': session['items']}
    else:
        logger.debug('''No items found in session, reply with {"items": null} \
JSON.''')
        return {'items': None}


@view_config(route_name='add_todo_list_item', request_method='POST')
def add_todo_list_item(request):
    """ Add new item to 'items' list in session memory.

    When request with POST method at /api/add_todo_list_item arrives then
    function checks if 'items' list esxists. If True - append new user item to
    the list, otherwise create new 'items' list in memory and add new item to
    it.

    :param request: instance of pyramid.request.Request class, which is
    created and put as arg for this function by router; represents HTTP
    request.
    :type request: instance
    :returns: instance of Response class with 'OK' string in it's body to
    indicate a success of performed procedures.

    """
    session = request.session
    logger.debug('Adding item "%s" to session.' % request.json_body['item'])
    if session.get('items'):
        session['items'].append(request.json_body['item'])
    else:
        session['items'] = []
        session['items'].append(request.json_body['item'])
    return Response('OK')
