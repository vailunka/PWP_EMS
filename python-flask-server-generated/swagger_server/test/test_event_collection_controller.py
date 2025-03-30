# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.event import Event  # noqa: E501
from swagger_server.test import BaseTestCase


class TestEventCollectionController(BaseTestCase):
    """EventCollectionController integration test stubs"""

    def test_events_get(self):
        """Test case for events_get

        List all events
        """
        response = self.client.open(
            '/api/events/',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_events_post(self):
        """Test case for events_post

        Create a new event
        """
        body = Event()
        response = self.client.open(
            '/api/events/',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
