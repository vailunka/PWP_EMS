import config as cfg
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import mysql.connector


# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = (f"mysql+pymysql://{cfg.DB_USERNAME}:{cfg.DB_PASSWORD}"
                                         f"@{cfg.DB_HOST}/{cfg.DB_NAME}")

# Initialize database
db = SQLAlchemy(app)


event_participants = db.Table("event_participants",
                              db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
                              db.Column("event_id", db.Integer, db.ForeignKey("event.id"), primary_key=True))


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(128), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(2048))
    organizer = db.Column(db.Integer, db.ForeignKey("user.id"))
    category = db.Column(db.JSON)
    tags = db.Column(db.JSON)

    users = db.relationship("User", secondary=event_participants, back_populates="attended_events")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(128), nullable=True)

    attended_events = db.relationship("Event", secondary=event_participants, back_populates="users")


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
