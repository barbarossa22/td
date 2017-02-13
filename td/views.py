"""
.. module:: views
   :platform: Unix
   :synopsis: Views for td app.

.. moduleauthor:: Mykola Radionov <moodaq@gmail.com>


"""


import logging
import os
import pymongo

from pyramid.httpexceptions import HTTPFound, HTTPForbidden, HTTPUnauthorized
from pyramid.response import FileResponse, Response
from pyramid.security import remember, forget, authenticated_userid

from td.password_master import PasswordMaster


logger = logging.getLogger(__name__)


def forbidden_view(request):
    return HTTPFound(location="/login")


def home(request):
    """Redirect from / to /todo_list url.

    :param request: instance-object which represents HTTP request.
    :type request: pyramid.request.Request
    :returns: HTTPFound exception as response object with status code 302.
    :raises: pyramid.httpexceptions.HTTPFound

    """
    logger.debug("Get request for the resource at / and redirected to "
                 "/todo_list url.")
    return HTTPFound(location="/todo_list")


def get_todo_list_page(request):
    """Return static/base.html at request on /todo_list url.

    :param request: instance-object which represents HTTP request.
    :type request: pyramid.request.Request
    :returns: object that is used to serve a file from static/base.html.
    :rtype: pyramid.response.FileResponse

    """
    logger.debug("Get request for resource at /todo_list and replied with "
                 "file static/base.html")
    abs_path_to_base = "".join([os.path.dirname(__file__),
                                os.sep,
                                os.path.join("static", "base.html")])
    return FileResponse(abs_path_to_base, cache_max_age=3600)


def get_todo_list_items(request):
    """Get JSON with list of todo-items from Mongo database at request on
    /api/get_todo_list_items url.

    :param request: instance-object which represents HTTP request.
    :type request: pyramid.request.Request
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
    logger.debug("Get request for todo list items at "
                 "/api/get_todo_list_items from user with ip %s",
                 ip)
    db = settings.db
    user_id = db.select_one("id", "Users", "ip='%s'" % ip)
    if user_id is None:
        logger.debug("This user is not in the database and that's why "
                     "items for him don't exist, reply with "
                     "{'items': null} JSON.")
        return {"items": None}
    else:
        user_id = user_id[0]
    mongo_creds = settings.mongo_creds
    client = pymongo.MongoClient(mongo_creds["host"],
                                 int(mongo_creds["port"]))
    db = client[mongo_creds["db_name"]]
    items_collection = db.Items
    reply = items_collection.find({"owner_id": user_id},
                                  {"item": 1, "_id": 0})
    items = [document["item"] for document in reply]
    logger.debug("Found existing items in the database, reply with "
                 "{'items': %s} JSON object.",
                 items)
    return {"items": items}


def add_todo_list_item(request):
    """ Add new item to the database.

    When request with POST method at /api/add_todo_list_item arrives then
    function checks if user's ip exists in the Postgres database table 'Users'.
    If no then raises HTTPUnauthorized.

    :param request: instance-object which represents HTTP request.
    :type request: pyramid.request.Request
    :returns: Response instance with 'OK' str body to indicate a success.
    :rtype: pyramid.response.Response

    """
    settings = request.registry.settings
    ip = request.client_addr
    logger.debug("User with ip %s is trying to add new item with POST "
                 "request on /api/add_todo_list_items",
                 ip)

    db = settings.db
    user_id = db.select_one("id", "Users", "ip='%s'" % ip)
    if user_id is None:
        return HTTPUnauthorized()
    mongo_creds = settings.mongo_creds
    client = pymongo.MongoClient(mongo_creds['host'],
                                 int(mongo_creds['port']))
    db = client[mongo_creds['db_name']]
    items_collection = db.Items
    items_collection.insert_one({"item": request.json_body["item"],
                                 "owner_id": user_id})

    logger.debug("Successfully added item '%s' to the database.",
                 request.json_body["item"])

    return Response("OK")


def get_login_page(request):
    """Return static/login.html at request on /login url.

    :param request: instance-object which represents HTTP request.
    :type request: pyramid.request.Request
    :returns: object that is used to serve a file from static/login.html.
    :rtype: pyramid.response.FileResponse
    """
    logger.debug("Get request for resource at /login and replied with "
                 "file static/login.html")
    abs_path_to_base = "".join([os.path.dirname(__file__),
                                os.sep,
                                os.path.join("static", "login.html")])
    return FileResponse(abs_path_to_base, cache_max_age=3600)


def post_login_credentials(request):
    """Accept POST request with login and password from the client.

    :param request: instance-object which represents HTTP request.
    :type request: pyramid.request.Request
    :returns: if ok HTTPFound with auth. headers in response else HTTPUnauthorized
    """
    login = request.json_body["login"]
    password = request.json_body["password"]
    ip = request.client_addr
    password_master = PasswordMaster()
    db = request.registry.settings.db
    query_output = db.select_one("password", "Users", "username='%s'" % login)

    if query_output is not None:
        hashed_pword_from_db = query_output[0]
        if password_master.check_password(password, hashed_pword_from_db):
            headers = remember(request, login)
            logger.debug("User %s has logged in right now.", login)
            return HTTPFound("/todo_list", headers=headers)
        else:
            logger.debug("Wrong password.")
            return HTTPUnauthorized()
    logger.debug("No such username in db.")
    return HTTPUnauthorized()


def logout(request):
    """Logout user.

    :param request: instance-object which represents HTTP request.
    :type request: pyramid.request.Request
    :returns: HTTPFound exception as response object with status code 302.
    :raises: pyramid.httpexceptions.HTTPFound
    """
    headers = forget(request)
    logger.debug("User %s logged out.", authenticated_userid(request))
    return HTTPFound(location="/login", headers=headers)
