import connexion
import six

from swagger_server.models.user import User  # noqa: E501
from swagger_server import util


def users_get():  # noqa: E501
    """List all users

     # noqa: E501


    :rtype: List[User]
    """
    return 'do some magic!'


def users_post(body):  # noqa: E501
    """Create a new user

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = User.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
