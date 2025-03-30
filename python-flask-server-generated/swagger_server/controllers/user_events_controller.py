import connexion
import six

from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server import util


def users_user_events_get(user):  # noqa: E501
    """Get all events a user organized or attended

     # noqa: E501

    :param user: Username as path parameter
    :type user: str

    :rtype: InlineResponse200
    """
    return 'do some magic!'
