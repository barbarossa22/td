import logging

from pyramid.httpexceptions import HTTPFound
from pyramid.response import FileResponse, Response
from pyramid.view import view_config


logger = logging.getLogger(__name__)


@view_config(route_name='home')
def my_view(request):
    logger.debug("""Get request for resource at / and redirected to /todo_list
url.""")
    return HTTPFound(location='/todo_list')


@view_config(route_name='todo_list', request_method='GET')
def get_todo_list_page(request):
    """Return web-page base.html on /todo_list url"""
    logger.debug("""Get request for resource at /todo_list and replied with
file static/base.html""")
    return FileResponse('/home/mrad/td/td/static/base.html', cache_max_age=3600)


@view_config(
    route_name='get_todo_list_items',
    renderer='json',
    request_method='GET'
)
def get_todo_list_items(request):
    """ Get list of items at /api/get_todo_list_items.

    If there are notes in current session memory return JSON in this format:
    {'items': ['sleep', 'eat', 'repeat']}
    Else: {'items': null}
    (in python code it looks like None, but later it'll be translated to JSON's
     null)
    """
    session = request.session
    logger.debug("Get request for todo list items at /api/get_todo_list_items")
    if 'items' in session:
        logger.debug("Found existing items in session memory, reply with {'items': %s} JSON object." % session['items'])
        return {'items': session['items']}
    else:
        logger.debug('No items found in session, reply with {"items": null} JSON.')
        return {'items': None}


@view_config(route_name='add_todo_list_item', request_method='POST')
def add_todo_list_item(request):
    """ Add item to the session memory at post request on
    /api/add_todo_list_item
    """
    session = request.session
    logger.debug('Adding item "%s" to session.' % request.json_body['item'])
    # del session['items']
    if 'items' in session:
        session['items'].append(request.json_body['item'])
    else:
        session['items'] = []
        session['items'].append(request.json_body['item'])
    return Response('OK')
