import connexion
import six

from swagger_server.models.event import Event  # noqa: E501
from swagger_server import util


def events_event_delete(event):  # noqa: E501
    """Delete an event

     # noqa: E501

    :param event: Event name as path parameter
    :type event: str

    :rtype: None
    """
    return 'do some magic!'


def events_event_get(event):  # noqa: E501
    """Get an event by name

     # noqa: E501

    :param event: Event name as path parameter
    :type event: str

    :rtype: Event
    """
    return 'do some magic!'


def events_event_put(body, event):  # noqa: E501
    """Update an event

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param event: Event name as path parameter
    :type event: str

    :rtype: None
    """
    if connexion.request.is_json:
        body = Event.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
