# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.test import BaseTestCase


class TestUserEventsController(BaseTestCase):
    """UserEventsController integration test stubs"""

    def test_users_user_events_get(self):
        """Test case for users_user_events_get

        Get all events a user organized or attended
        """
        response = self.client.open(
            '/api/users/{user}/events/'.format(user='user_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
