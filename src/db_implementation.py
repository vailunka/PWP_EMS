"""This file contains the database implementation, including all the models and resources, etc."""

from datetime import datetime
import jsonschema.validators
from jsonschema import validate, ValidationError
from flask import Flask, request, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import NotFound, BadRequest
import mysql.connector
import config as cfg


# Initialize Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{cfg.DB_USERNAME}:{cfg.DB_PASSWORD}"
    f"@{cfg.DB_HOST}/{cfg.DB_NAME}"
)

# Initialize database
db = SQLAlchemy(app)
api = Api(app)


def create_database():
    """Creates the MySQL database with the name cfg.DB_NAME"""
    database = mysql.connector.connect(
        host=cfg.DB_HOST, user=cfg.DB_USERNAME, passwd=cfg.DB_PASSWORD
    )
    database_cursor = database.cursor()
    try:
        database_cursor.execute(f"CREATE DATABASE {cfg.DB_NAME}")
    except mysql.connector.errors.DatabaseError as db_error:
        print(f"{db_error.__class__.__name__}:{db_error}")
        print("DROPPING EXISTING DB AND RECREATING IT")
        database_cursor.execute(f"DROP DATABASE {cfg.DB_NAME}")
        database_cursor.execute(f"CREATE DATABASE {cfg.DB_NAME}")


event_participants = db.Table(
    "event_participants",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("event_id", db.Integer, db.ForeignKey("event.id"), primary_key=True),
)


class Event(db.Model):
    """
    Model for the Events.
    Mandatory attributes are name, location, time and organizer.
    Optional parameters are description, category and tags
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(128), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    organizer = db.Column(db.Integer, db.ForeignKey("user.id"))
    description = db.Column(db.String(2048))
    category = db.Column(db.JSON)
    tags = db.Column(db.JSON)

    users = db.relationship("User", secondary=event_participants, back_populates="attended_events")

    def serialize(self, short_form=False):
        """
        Creates a dictionary of Event's attributes.

        :param bool short_form: Returns a short dictionary if True, default is False.
        :returns dict serialized: Serialized data in dictionary form.
        """
        serialized = {
            "name": self.name,
            "location": self.location,
            "time": datetime.isoformat(self.time),
            "organizer": self.organizer
        }
        if not short_form:
            serialized["description"] = self.description
            serialized["category"] = self.category
            serialized["tags"] = self.tags
        return serialized

    def deserialize(self, serialized_data):
        """
        Assigns Event object attribute values based on the given dictionary.

        :param dict serialized_data: Dictionary containing the information to be deserialized.
        """
        self.name = serialized_data["name"]
        self.location = serialized_data["location"]
        self.time = datetime.fromisoformat(serialized_data["time"])
        self.organizer = serialized_data["organizer"]
        # Optional parameters
        self.description = serialized_data.get("description")
        self.category = serialized_data.get("category")
        self.tags = serialized_data.get("tags")

    @staticmethod
    def json_schema():
        """
        Creates a JSON schema for Event

        :return dict schema: Returns the JSON schema
        """
        schema = {
            "type": "object",
            "required": ["name", "location", "time", "organizer"]
        }
        properties = schema["properties"] = {}
        properties["name"] = {"description": "Name of the event", "type": "string"}
        properties["location"] = {
            "description": "Location of the event",
            "type": "string"
        }
        properties["time"] = {
            "description": "Time of the event",
            "type": "string",
            "format": "date-time"
        }
        properties["organizer"] = {
            "description": "ID of the user who is organizing the event",
            "type": "integer",
            "minimum": 0
        }
        return schema


class User(db.Model):
    """
    Model for a user.
    Mandatory attributes are name and email, optional parameter is phone_number.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(128), nullable=True)

    attended_events = db.relationship(
        "Event", secondary=event_participants, back_populates="users"
    )

    def serialize(self, short_form=False):
        """
        Creates a dictionary of User's attributes.

        :param bool short_form: Returns a short dictionary if True, default is False.
        :returns dict serialized: Serialized data in dictionary form.
        """
        serialized = {"name": self.name, "email": self.email}
        if not short_form:
            serialized["phone_number"] = self.phone_number
        return serialized

    def deserialize(self, serialized_data):
        """
        Assigns User object attribute values based on the given dictionary.

        :param dict serialized_data: Dictionary containing the information to be deserialized.
        """
        self.name = serialized_data["name"]
        self.email = serialized_data["email"]
        # Optional parameter
        self.phone_number = serialized_data.get("phone_number")

    @staticmethod
    def json_schema():
        """
        Creates a JSON schema for User

        :return dict schema: Returns the JSON schema
        """
        schema = {"type": "object", "required": ["name", "email"]}
        properties = schema["properties"] = {}
        properties["name"] = {"description": "Name of the user", "type": "string"}
        properties["email"] = {"description": "Email of the user", "type": "string"}
        return schema


# User-related resources
class UserItem(Resource):
    """
    A flask-restful Resource that contains GET, PUT and DELETE HTTP methods for an individual user.
    """

    def get(self, user):
        """
        Handles the GET HTTP method. Gets information about the user.

        :param User user: User object
        :returns Response: Response object containing
        """
        response = jsonify(user.serialize())
        response.status_code = 200
        return response

    def put(self, user):
        """
        Handles the PUT HTTP method. PUTs/updates an existing user.

        :param User user: User object
        :returns Response: Response object containing different statuses depending on success.
        """
        contents = request.json
        try:
            validate(
                instance=contents,
                schema=User.json_schema(),
                format_checker=jsonschema.validators.Draft7Validator.FORMAT_CHECKER
            )
        except ValidationError as ex:
            raise BadRequest(description=str(ex))
        user.deserialize(contents)
        db.session.commit()
        url = api.url_for(UserItem, user=user)
        return Response(response=url, status=201)

    def delete(self, user):
        """
        Handles the DELETE HTTP method. Deletes the user from the database.
        If user is an organizer of any event, deletes the event(s) created by the user
        before deleting the user.

        :param User user: User object
        :return Response: Response object with status 204 if successful
        """
        # Check if user is an organizer of events, and if yes, delete the events first.
        events_organized_by_user = Event.query.filter_by(organizer=user.id).all()
        if events_organized_by_user:
            for event in events_organized_by_user:
                db.session.delete(event)
            db.session.commit()
        db.session.delete(user)
        db.session.commit()
        return Response(status=204)


class UserCollection(Resource):
    """
    A flask-restful Resource that contains GET and POST HTTP methods for all the users.
    """

    def get(self):
        """
        Handles the GET HTTP method. Gets information about all the users.

        :returns List: List of serialized users
        """
        users = User.query.all()
        serialized_users = [user.serialize() for user in users]
        return serialized_users

    def post(self):
        """
        Handles the POST HTTP method. Creates a new user based on given values in the POST request.

        :returns response: Response with the dictionary containing the values for created user.
        """
        contents = request.json
        try:
            validate(
                instance=contents,
                schema=User.json_schema(),
                format_checker=jsonschema.validators.Draft7Validator.FORMAT_CHECKER,
            )
        except ValidationError as ex:
            raise BadRequest(description=str(ex))
        user = User()
        user.deserialize(contents)
        db.session.add(user)
        db.session.commit()
        url = api.url_for(UserItem, user=user)
        response = jsonify(user.serialize())
        response.status_code = 201
        response.headers["location"] = url
        return response


class UserEvents(Resource):
    """
    A flask-restful Resource that contains a GET HTTP method for events that user has attended
    or organized.
    """

    def get(self, user):
        """
        Handles the GET HTTP method. Gets information about the events
        user has attended and/or organized.

        :returns Response: Response containing the events user has organized or attended.
        """
        events_organized_by_user = Event.query.filter_by(organizer=user.id).all()
        attended_events_json = []
        for event in user.attended_events:
            attended_events_json.append(event.serialize())

        organized_events_json = []
        for event in events_organized_by_user:
            organized_events_json.append(event.serialize())

        # Serialize response
        event_infos = {
            "attended_events": attended_events_json,
            "organized_events": organized_events_json,
        }
        # Generate URL
        url = api.url_for(UserEvents, user=user)

        response = jsonify({"user_name": user.name, "event_infos": event_infos})
        response.status_code = 200
        response.headers["Location"] = url
        return response


# Event-related resources
class EventItem(Resource):
    """
    A flask-restful Resource that contains the GET, PUT and DELETE HTTP methods
    for individual events.
    """

    def get(self, event):
        """
        Handles the GET HTTP method. Gets information about an individual event.

        :returns Response: Response containing the event information
        """
        response = jsonify(event.serialize())
        response.status_code = 200
        return response

    def put(self, event):
        """
        Handles the PUT HTTP method. PUTs/modifies an existing event.

        :returns Response: Response containing the event information
        """
        contents = request.json
        try:
            validate(
                instance=contents,
                schema=Event.json_schema(),
                format_checker=jsonschema.validators.Draft7Validator.FORMAT_CHECKER,
            )
        except ValidationError as ex:
            raise BadRequest(description=str(ex))
        event.deserialize(contents)
        db.session.commit()
        url = api.url_for(EventItem, event=event)
        return Response(response=url, status=200)

    def delete(self, event):
        """
        Handles the DELETE HTTP method. Deletes an event.

        :returns Response: Response with status code 204
        """
        db.session.delete(event)
        db.session.commit()
        return Response(status=204)


class EventCollection(Resource):
    """
    A flask-restful Resource that contains the GET and POST HTTP methods for all events.
    """

    def get(self):
        """
        Handles the GET HTTP method. Gets information about all the events.

        :returns List: Returns a list of serialized events.
        """
        events = Event.query.all()
        serialized_events = [event.serialize() for event in events]
        return serialized_events

    def post(self):
        """
        Handles the POST HTTP method. Creates a new event based on given values in the POST request.

        :returns Response: Response with the serialized information about the event with
                           a status code
        """
        contents = request.json
        # Validation
        try:
            validate(
                instance=contents,
                schema=Event.json_schema(),
                format_checker=jsonschema.validators.Draft7Validator.FORMAT_CHECKER,
            )
        except ValidationError as ex:
            raise BadRequest(description=str(ex))

        # Check if an event with the same name already exists
        # existing_event = Event.query.filter_by(name=contents["name"]).first()
        # if existing_event:
        #    return Response(status=409)

        e = Event()
        e.deserialize(contents)
        db.session.add(e)
        db.session.commit()

        # Return the response with the location header
        url = api.url_for(EventItem, event=e)

        response = jsonify(e.serialize())
        response.status_code = 201
        response.headers["location"] = url
        return response


# Converters
class UserConverter(BaseConverter):
    """
    A werkzeug routing BaseConverter converter that is used to map User objects to an url
    and vice-versa.
    """

    def to_python(self, value):
        db_user = User.query.filter_by(name=value).first()
        if not db_user:
            raise NotFound
        return db_user

    def to_url(self, value):
        return value.name


class EventConverter(BaseConverter):
    """
    A werkzeug routing BaseConverter converter that is used to map Event objects to an url
    and vice-versa.
    """

    def to_python(self, value):
        db_event = Event.query.filter_by(name=value).first()
        if not db_event:
            raise NotFound
        return db_event

    def to_url(self, value):
        return value.name


# Converter mappings
app.url_map.converters["user"] = UserConverter
app.url_map.converters["event"] = EventConverter

# Endpoints, NOTE: not sure if .../users/... is a needed endpoint
api.add_resource(UserCollection, "/api/users/")
api.add_resource(UserItem, "/api/<user:user>/", "/api/users/<user:user>/")
api.add_resource(
    UserEvents, "/api/<user:user>/events/", "/api/users/<user:user>/events/"
)
api.add_resource(EventCollection, "/api/events/")
api.add_resource(EventItem, "/api/events/<event:event>/")
