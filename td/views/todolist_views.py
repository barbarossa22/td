"""
.. module:: todolist_views
   :platform: Unix
   :synopsis: Views for td app todolist CRD operations.

.. moduleauthor:: Mykola Radionov <moodaq@gmail.com>


"""


import logging
import os
import pymongo

from bson import ObjectId
from pyramid.httpexceptions import (HTTPFound,
                                    HTTPUnauthorized,
                                    HTTPInternalServerError)
from pyramid.response import FileResponse, Response
from pyramid.security import authenticated_userid
from pyramid.view import view_defaults


logger = logging.getLogger(__name__)


@view_defaults(permission="entry")
class TodolistViews(object):

    def __init__(self, request):
        self.request = request

    def home(self):
        """Redirect from / to /todo_list url.

        :returns: HTTPFound exception as response object with status code 302.
        :rtype: pyramid.httpexceptions.HTTPFound
        """
        logger.debug("Get request for the resource at / and redirected to "
                     "/todo_list url.")
        return HTTPFound(location="/todo_list")

    def get_todo_list_page(self):
        """Return static/base.html at request on /todo_list url.

        :returns: object that is used to serve a file from static/base.html.
        :rtype: pyramid.response.FileResponse

        """
        logger.debug("Get request for resource at /todo_list and replied with "
                     "file static/base.html")
        abs_path_to_base = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                        "static",
                                        "base.html")

        return FileResponse(path=abs_path_to_base, cache_max_age=3600)

    def get_todo_list_items(self):
        """Get JSON with list of todo-items from Mongo database at request on
        /api/get_todo_list_items url.

        :returns: dict that is later transformed by json-renderer into response
        object with included JSON-serialized string made from this dict:

        * {'items': [{'item_value': 'sleep', 'category': 'green'},
                     {'item_value': 'eat', 'category': 'red'},
                     {'item_value': 'repeat', 'category': 'yellow'}
                    ]} or similar user-defined notes in list if they exist in
        the database;

        * {'items': None} otherwise, if items for user with current id doesn't
        exist.
        :rtype: dict

        """
        settings = self.request.registry.settings
        ip = self.request.client_addr
        login_name = authenticated_userid(self.request)
        logger.debug("Get request for todo list items at "
                     "/api/get_todo_list_items from user with ip %s and "
                     "username '%s'", ip, login_name)
        db = settings["db"]

        user_int_id = db.select_one("id",
                                    "Users",
                                    "username='%s'" % login_name)
        if user_int_id is None:
            return HTTPUnauthorized()
        # extract id integer from tuple like (2,)[0] -> 2
        user_int_id = user_int_id[0]

        mongo_creds = settings["mongo_creds"]
        try:
            client = pymongo.MongoClient(mongo_creds["host"],
                                         int(mongo_creds["port"]))
        except pymongo.errors.ConnectionFailure, error_msg:
            logger.debug("Cannot connect to mongodb with given config "
                         "credentials due to the next reason:"
                         "\n%s", error_msg)
            return HTTPInternalServerError()
        mongo_db = client[mongo_creds["db_name"]]
        items_collection = mongo_db.Items
        reply = items_collection.find({"owner_id": user_int_id},
                                      {"item_value": 1,
                                       "category": 1,
                                       "_id": 1})
        items = [{"item_value": document["item_value"],
                  "category": document["category"],
                  "id": str(document["_id"])}
                 for document in reply]
        if len(items) == 0:
            logger.debug("Items for this user don't exist, reply with "
                         "{'items': null} JSON.")
            return {"items": None}
        logger.debug("Found existing items in the database, reply with "
                     "{'items': %s} JSON object.", items)
        return {"items": items}

    def add_todo_list_item(self):
        """Add new item to the database.

        When request with POST method at /api/add_todo_list_item arrives then
        function checks if user's id exists in the Postgres database table
        'Users'. If no then raises HTTPUnauthorized.

        :returns: Response instance with 'OK' str body to indicate a success.
        :rtype: pyramid.response.Response

        """
        settings = self.request.registry.settings
        ip = self.request.client_addr
        login_name = authenticated_userid(self.request)
        logger.debug("User with ip %s and username '%s' is trying to add new "
                     "item with POST request on /api/add_todo_list_items",
                     ip, login_name)

        db = settings["db"]
        user_int_id = db.select_one("id",
                                    "Users",
                                    "username='%s'" % login_name)
        if user_int_id is None:
            return HTTPUnauthorized()
        # extract id integer from tuple like (2,)[0] -> 2
        user_int_id = user_int_id[0]
        mongo_creds = settings["mongo_creds"]
        client = pymongo.MongoClient(mongo_creds['host'],
                                     int(mongo_creds['port']))
        mongo_db = client[mongo_creds['db_name']]
        items_collection = mongo_db.Items
        items_collection.insert_one({"item_value": self.request.json_body["item_value"],
                                     "category": self.request.json_body["category"],
                                     "owner_id": user_int_id})
        logger.debug("Successfully added item '%s' to the database.",
                     self.request.json_body["item_value"])

        return Response("OK")

    def remove_item(self):
        """Delete item from database by id.

        :returns: Response instance with 'OK' str body to indicate a success.
        :rtype: pyramid.response.Response
        """
        _id = ObjectId(self.request.json_body['id'])

        settings = self.request.registry.settings
        mongo_creds = settings["mongo_creds"]
        client = pymongo.MongoClient(mongo_creds['host'],
                                     int(mongo_creds['port']))
        mongo_db = client[mongo_creds['db_name']]
        items_collection = mongo_db.Items
        items_collection.delete_one({"_id": _id})
        logger.debug("Removing item from mongo db with id: %s", _id)
        return Response("OK")
