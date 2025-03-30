import connexion
import six

from swagger_server.models.user import User  # noqa: E501
from swagger_server import util


def users_user_delete(user):  # noqa: E501
    """Delete a user

     # noqa: E501

    :param user: Username as path parameter
    :type user: str

    :rtype: None
    """
    return 'do some magic!'


def users_user_get(user):  # noqa: E501
    """Get a user by name

     # noqa: E501

    :param user: Username as path parameter
    :type user: str

    :rtype: User
    """
    return 'do some magic!'


def users_user_put(body, user):  # noqa: E501
    """Update a user

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param user: Username as path parameter
    :type user: str

    :rtype: None
    """
    if connexion.request.is_json:
        body = User.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
