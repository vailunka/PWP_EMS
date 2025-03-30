# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.user import User  # noqa: E501
from swagger_server.test import BaseTestCase


class TestUserItemController(BaseTestCase):
    """UserItemController integration test stubs"""

    def test_users_user_delete(self):
        """Test case for users_user_delete

        Delete a user
        """
        response = self.client.open(
            '/api/users/{user}/'.format(user='user_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_users_user_get(self):
        """Test case for users_user_get

        Get a user by name
        """
        response = self.client.open(
            '/api/users/{user}/'.format(user='user_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_users_user_put(self):
        """Test case for users_user_put

        Update a user
        """
        body = User()
        response = self.client.open(
            '/api/users/{user}/'.format(user='user_example'),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
