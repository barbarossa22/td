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

from td.assessors.assessors import DbAssessor


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
    :returns: object that is used to serve a file from static/base.html.
    :rtype: pyramid.response.FileResponse

    """
    logger.debug('''Get request for resource at /todo_list and replied with \
file static/base.html''')
    abs_path_to_base = ''.join(
        [
            os.path.dirname(__file__),
            os.sep,
            os.path.join('static', 'base.html')
        ]
    )
    return FileResponse(abs_path_to_base, cache_max_age=3600)


@view_config(
    route_name='get_todo_list_items',
    renderer='json',
    request_method='GET'
)
def get_todo_list_items(request):
    """Get JSON with list of todo-items from MySQL database at request on
    /api/get_todo_list_items url.

    :param request: instance-object which represents HTTP request.
    :type: pyramid.request.Request
    :returns: dict that is later transformed by json-renderer into response
    object with included JSON-serialized string made from this dict:

    * {'items': ['sleep', 'eat', 'repeat']} or similar user-defined notes in
    list if they exist in the database;

    * {'items': None} otherwise, if items for user with current ip doesn't
    exist.
    :rtype: dict

    """
    settings = request.registry.settings
    ip = request.client_addr
    logger.debug(
        '''Get request for todo list items at /api/get_todo_list_items from \
user with ip %s''', ip
    )
    with DbAssessor(
        settings.db_host, settings.db_user,
        settings.db_password, settings.db_name
    ) as db:
        cursor = db.cursor
        cursor.execute("SELECT id FROM Users WHERE ip=%s", (ip,))
        user_id = cursor.fetchone()
        if user_id is None:
            logger.debug(
                '''No items for current user found in the database, reply \
with {"items": null} JSON.'''
            )
            return {'items': None}
        cursor.execute(
            'SELECT item from Items WHERE owner_id=%s', (user_id[0],)
        )
        select_query_output = cursor.fetchall()
        items = [item[0] for item in select_query_output]
        logger.debug(
            '''Found existing items in the database, reply with \
{'items': %s} JSON object.''', items
        )
        return {'items': items}


@view_config(route_name='add_todo_list_item', request_method='POST')
def add_todo_list_item(request):
    """ Add new item to the database.

    When request with POST method at /api/add_todo_list_item arrives then
    function checks if user's ip exists in the databases table 'Users'. If no
    then it creates new entry for him in 'Users' table and after that appends
    to the table 'Items' his todo list item from POST json body.

    :param request: instance-object which represents HTTP request.
    :type: pyramid.request.Request
    :returns: Response instance with 'OK' str body to indicate a success.
    :rtype: pyramid.response.Response

    """
    settings = request.registry.settings
    ip = request.client_addr
    logger.debug('User with ip %s is trying to add new items with POST \
request on /api/add_todo_list_items', ip)

    with DbAssessor(
        settings.db_host, settings.db_user,
        settings.db_password, settings.db_name
    ) as db:
        cursor = db.cursor

        cursor.execute("SELECT id FROM Users WHERE ip=%s", (ip,))
        user_id = cursor.fetchone()
        if user_id is None:
            logger.debug('''User with such ip does not exist in the database,\
            creating new entry for him in Users table''')
            cursor.execute("INSERT INTO Users(ip) VALUES (%s)", (ip,))
            cursor.execute("SELECT id FROM Users WHERE ip=%s", (ip,))
            user_id = cursor.fetchone()[0]

        cursor.execute(
            "INSERT INTO Items(item, owner_id) VALUES (%s, %s)",
            (request.json_body['item'], user_id)
        )

        db.commit()

        logger.debug(
            'Successfully added item "%s" to the database.',
            request.json_body['item']
        )

    return Response('OK')
