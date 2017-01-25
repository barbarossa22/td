"""
.. module:: test_views
   :platform: Unix
   :synopsis: Unittests for td.views

.. moduleauthor:: Mykola Radionov <moodaq@gmail.com>


"""

import unittest
import mock

from pyramid import testing

from td import views


class TestItemsGetting(unittest.TestCase):
    """Test views.get_todo_list_items with mock patches of db output."""
    def setUp(self):
        self.request = testing.DummyRequest()
        self.request.client_addr = '127.127.127.127'

        class EmptyObj:
            pass
        self.request.registry.settings = EmptyObj()
        self.request.registry.settings.db_host = 'localhost'
        self.request.registry.settings.db_user = 'root'
        self.request.registry.settings.db_password = '789456123'
        self.request.registry.settings.db_name = 'TDDB'

    @mock.patch('td.views.DbAssessor')
    def test_nonexisting_items_getting(self, assessor):
        """Test views.get_todo_list_items with nonexisting ip in Users
        table (and that's why nonexisting items too).
        """
        fake_db = assessor.return_value.__enter__.return_value
        fake_db.cursor.fetchone.return_value = None
        response = views.get_todo_list_items(self.request)
        self.assertEqual(response, {'items': None})

    @mock.patch('td.views.DbAssessor')
    def test_existing_items_getting(self, assessor):
        """Test views.get_todo_list_items with existing items obj in
        database with value ['one', '2'].
        """
        fake_db = assessor.return_value.__enter__.return_value
        fake_db.cursor.fetchone.return_value = 'Not none'
        fake_db.cursor.fetchall.return_value = (('one',), ('2',))
        response = views.get_todo_list_items(self.request)
        self.assertEqual(response, {'items': ['one', '2']})


class TestItemsAdding(unittest.TestCase):
    """Test views.add_todo_list_item"""

    def setUp(self):
        """Create DummyRequest and fake data in json_body for each test."""
        self.request = testing.DummyRequest()
        self.request.json_body = {'item': 'wake up'}
        self.request.client_addr = '127.0.0.1'
        self.request.registry.settings = {}

    def test_adding_to_nonexisting_items_list(self):
        """Test views.add_todo_list_item with nonexisting items obj in
        session.
        """
        response = views.add_todo_list_item(self.request)
        self.assertIn('items', self.request.session)
        self.assertEqual(self.request.session.get('items'), ['wake up'])
        self.assertEqual(response.body, 'OK')

    def test_adding_to_existing_items_list(self):
        """Test views.add_todo_list_item with existing items obj in
        session and ['old item'] in it.
        """
        self.request.session['items'] = ['old item']
        response = views.add_todo_list_item(self.request)
        self.assertIn('items', self.request.session)
        self.assertEqual(
            self.request.session.get('items'), ['old item', 'wake up']
        )
        self.assertEqual(response.body, 'OK')


class TestHomeIndex(unittest.TestCase):
    """Test views.home"""

    def setUp(self):
        """Create DummyRequest for the test."""
        self.request = testing.DummyRequest()
        self.request.client_addr = '127.0.0.1'

    def test_redirection(self):
        """Test views.home by checking if redirection to /todo_list url was
        performed.
        """
        response = views.home(self.request)
        self.assertEqual(response.code, 302)
        self.assertEqual(response.location, '/todo_list')


class TestTodoListPageGetting(unittest.TestCase):
    """Test views.get_todo_list_page"""

    def setUp(self):
        """Create DummyRequest for the test."""
        self.request = testing.DummyRequest()

    def test_page_getting(self):
        """Test views.get_todo_list_page by checking if FileResponse is done
        with known html code in it's body.
        """
        response = views.get_todo_list_page(self.request)
        self.assertIn(
            '<div id="add_item_panel" class="input-group">', response.body
        )
