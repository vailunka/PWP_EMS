# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.inline_response200_event_infos import InlineResponse200EventInfos  # noqa: F401,E501
from swagger_server import util


class InlineResponse200(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, user_name: str=None, event_infos: InlineResponse200EventInfos=None):  # noqa: E501
        """InlineResponse200 - a model defined in Swagger

        :param user_name: The user_name of this InlineResponse200.  # noqa: E501
        :type user_name: str
        :param event_infos: The event_infos of this InlineResponse200.  # noqa: E501
        :type event_infos: InlineResponse200EventInfos
        """
        self.swagger_types = {
            'user_name': str,
            'event_infos': InlineResponse200EventInfos
        }

        self.attribute_map = {
            'user_name': 'user_name',
            'event_infos': 'event_infos'
        }
        self._user_name = user_name
        self._event_infos = event_infos

    @classmethod
    def from_dict(cls, dikt) -> 'InlineResponse200':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The inline_response_200 of this InlineResponse200.  # noqa: E501
        :rtype: InlineResponse200
        """
        return util.deserialize_model(dikt, cls)

    @property
    def user_name(self) -> str:
        """Gets the user_name of this InlineResponse200.


        :return: The user_name of this InlineResponse200.
        :rtype: str
        """
        return self._user_name

    @user_name.setter
    def user_name(self, user_name: str):
        """Sets the user_name of this InlineResponse200.


        :param user_name: The user_name of this InlineResponse200.
        :type user_name: str
        """

        self._user_name = user_name

    @property
    def event_infos(self) -> InlineResponse200EventInfos:
        """Gets the event_infos of this InlineResponse200.


        :return: The event_infos of this InlineResponse200.
        :rtype: InlineResponse200EventInfos
        """
        return self._event_infos

    @event_infos.setter
    def event_infos(self, event_infos: InlineResponse200EventInfos):
        """Sets the event_infos of this InlineResponse200.


        :param event_infos: The event_infos of this InlineResponse200.
        :type event_infos: InlineResponse200EventInfos
        """

        self._event_infos = event_infos
