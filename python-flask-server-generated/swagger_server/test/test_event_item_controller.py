# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.event import Event  # noqa: E501
from swagger_server.test import BaseTestCase


class TestEventItemController(BaseTestCase):
    """EventItemController integration test stubs"""

    def test_events_event_delete(self):
        """Test case for events_event_delete

        Delete an event
        """
        response = self.client.open(
            '/api/events/{event}/'.format(event='event_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_events_event_get(self):
        """Test case for events_event_get

        Get an event by name
        """
        response = self.client.open(
            '/api/events/{event}/'.format(event='event_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_events_event_put(self):
        """Test case for events_event_put

        Update an event
        """
        body = Event()
        response = self.client.open(
            '/api/events/{event}/'.format(event='event_example'),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
