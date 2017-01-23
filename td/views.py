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

    :param request: instance-object which represents HTTP request.
    :type: pyramid.request.Request
    :returns: HTTPFound exception as response object with status code 302.
    :raises: pyramid.httpexceptions.HTTPFound

    """
    logger.debug('''Get request for the resource at / and redirected to \
/todo_list url.''')
    return HTTPFound(location='/todo_list')


@view_config(route_name='todo_list', request_method='GET')
def get_todo_list_page(request):
    """Return static/base.html at request on /todo_list url.

    :param request: instance-object which represents HTTP request.
    :type: pyramid.request.Request
    :returns: object that is used to serve a file froml static/base.html.
    :rtype: pyramid.response.FileResponse

    """
    logger.debug('''Get request for resource at /todo_list and replied with \
file static/base.html''')
    abs_path_to_base = ''.join(
        [os.path.dirname(__file__), os.sep, os.path.join('static', 'base.html')]
    )
    return FileResponse(abs_path_to_base, cache_max_age=3600)


@view_config(
    route_name='get_todo_list_items',
    renderer='json',
    request_method='GET'
)
def get_todo_list_items(request):
    """Get JSON with list of todo-items from session memory at request on
    /api/get_todo_list_items url.

    :param request: instance-object which represents HTTP request.
    :type: pyramid.request.Request
    :returns: dict that is later transformed by json-renderer into response
    object with included JSON-serialized string made from this dict:

    * {'items': ['sleep', 'eat', 'repeat']} or similar user-defined notes in
    list if they exist in session memory;

    * {'items': None} otherwise, if 'items' list doesn't exist.
    :rtype: dict

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

    :param request: instance-object which represents HTTP request.
    :type: pyramid.request.Request
    :returns: Response instance with 'OK' str body to indicate a success.
    :rtype: pyramid.response.Response

    """
    session = request.session
    logger.debug('Adding item "%s" to session.' % request.json_body['item'])
    if session.get('items'):
        session['items'].append(request.json_body['item'])
    else:
        session['items'] = []
        session['items'].append(request.json_body['item'])
    return Response('OK')
