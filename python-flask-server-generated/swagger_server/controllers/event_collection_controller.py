import connexion
import six

from swagger_server.models.event import Event  # noqa: E501
from swagger_server import util


def events_get():  # noqa: E501
    """List all events

     # noqa: E501


    :rtype: List[Event]
    """
    return 'do some magic!'


def events_post(body):  # noqa: E501
    """Create a new event

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = Event.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
