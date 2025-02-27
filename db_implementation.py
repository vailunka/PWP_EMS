import config as cfg
import jsonschema.validators
from jsonschema import validate, ValidationError
from flask import Flask, request, abort, Response
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from sqlalchemy.exc import IntegrityError
from sqlalchemy import event
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import NotFound, BadRequest
from datetime import datetime
import mysql.connector


# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = (f"mysql+pymysql://{cfg.DB_USERNAME}:{cfg.DB_PASSWORD}"
                                         f"@{cfg.DB_HOST}/{cfg.DB_NAME}")

# Initialize database
db = SQLAlchemy(app)
api = Api(app)


def create_database():
    """Creates the MySQL database with the name cfg.DB_NAME"""
    database = mysql.connector.connect(host=cfg.DB_HOST, user=cfg.DB_USERNAME, passwd=cfg.DB_PASSWORD)
    database_cursor = database.cursor()
    try:
        database_cursor.execute(f"CREATE DATABASE {cfg.DB_NAME}")
    except mysql.connector.errors.DatabaseError as db_error:
        print(f"{db_error.__class__.__name__}:{db_error}")
        print("DROPPING EXISTING DB AND RECREATING IT")
        database_cursor.execute(f"DROP DATABASE {cfg.DB_NAME}")
        database_cursor.execute(f"CREATE DATABASE {cfg.DB_NAME}")


event_participants = db.Table("event_participants",
                              db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
                              db.Column("event_id", db.Integer, db.ForeignKey("event.id"), primary_key=True))


class Event(db.Model):
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
        serialized = {"name": self.name,
                      "location": self.location,
                      "time": self.time,
                      "organizer": self.organizer}
        if not short_form:
            serialized['description'] = self.description,
            serialized['category'] = self.category,
            serialized['tags'] = self.tags
        return serialized

    def deserialize(self, serialized_data):
        self.name = serialized_data['name']
        self.location = serialized_data['location']
        self.time = datetime.fromisoformat(serialized_data['time'])
        self.organizer = serialized_data['organizer']
        # Optional parameters
        self.description = serialized_data.get('description')
        self.category = serialized_data.get('category')
        self.tags = serialized_data.get('tags')

    @staticmethod
    def json_schema():
        schema = {
            "type": "object",
            "required": ["name", "location", "time", "organizer"]
        }
        properties = schema['properties'] = {}
        properties['name'] = {
            "description": "Name of the event",
            "type": "string"
        }
        properties['location'] = {
            "description": "Location of the event",
            "type": "string"
        }
        properties['time'] = {
            "description": "Time of the event",
            "type": "date"
        }
        properties['organizer'] = {
            "description": "ID of the user who is organizing the event",
            "type": "integer",
            "minimum": 0
        }
        return schema


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(128), nullable=True)

    attended_events = db.relationship("Event", secondary=event_participants, back_populates="users")

    def serialize(self, short_form=False):
        serialized = {"name": self.name,
                      "email": self.email}
        if not short_form:
            serialized['phone_number'] = self.phone_number
        return serialized

    def deserialize(self, serialized_data):
        self.name = serialized_data['name']
        self.email = serialized_data['email']
        # Optional parameter
        self.phone_number = serialized_data['phone_number']

    @staticmethod
    def json_schema():
        schema = {
            "type": "object",
            "required": ["name", "email"]
        }
        properties = schema['properties'] = {}
        properties['name'] = {
            "description": "Name of the user",
            "type": "string"
        }
        properties['email'] = {
            "description": "Email of the user",
            "type": "string"
        }
        return schema


# User-related resources
class UserItem(Resource):

    def get(self, user):
        db_user = User.query.filter_by(name=user.name).first()
        if not db_user:
            raise NotFound

    def put(self, user):
        pass

    def post(self, user):
        pass


class UserCollection(Resource):

    def get(self):
        pass

    def put(self):
        pass

    def post(self):
        pass

    def delete(self):
        pass


class UserEvents(Resource):

    # Check which methods are required here
    # maybe only get to query the events the user has attended + organized
    def get(self, user_name):
        user = User.query.filter_by(name=user_name).first()
        if not user:
            raise NotFound
        events_organized_by_user = Event.query.filter_by(organizer=user.id).all()
        event_infos = {
            "attended_events": user.attended_events,
            "organized_events": events_organized_by_user
        }
        return Response("", 201, {"user_name": user.name, "event_infos": event_infos})

    def delete(self):
        pass


# Event-related resources
class EventItem(Resource):
    pass


class EventCollection(Resource):
    pass


# Converters
class UserConverter(BaseConverter):

    def to_python(self, user_name):
        db_user = User.query.filter_by(name=user_name).first()
        if not db_user:
            raise NotFound
        return db_user

    def to_url(self, db_user):
        return db_user.name


class EventConverter(BaseConverter):

    def to_python(self, event_id):
        db_event = Event.query.filter_by(id=event_id).first()
        if not db_event:
            raise NotFound
        return db_event

    def to_url(self, db_event):
        return db_event.name


# Converter mappings
app.url_map.converters["user"] = UserConverter
app.url_map.converters["event"] = EventConverter

# Endpoints, NOTE: not sure if .../users/... is a needed endpoint
api.add_resource(UserCollection, "/api/users/")
api.add_resource(UserItem, "/api/<user:user>/", "/api/users/<user:user>/")
api.add_resource(UserEvents, "/api/<user:user>/events/", "/api/users/<user:user>/events/")
api.add_resource(EventCollection, "/api/events/")
api.add_resource(EventItem, "/api/events/<event:event>/")
