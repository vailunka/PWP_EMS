import os
import random
import config as cfg
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Engine
from sqlalchemy import event
from datetime import datetime
from faker import Faker
import mysql.connector


fake = Faker()


def populate_database():
    # Populating random.randint() amount of users with fake data
    user_amount = random.randint(5, 30)
    event_amount = random.randint(4, 10)
    print(f"Amount of users: {user_amount}\nAmount of events: {event_amount}")
    for _ in range(user_amount):
        user = User(name=fake.name(), email=fake.email(), phone_number=fake.phone_number())
        db.session.add(user)
    db.session.commit()
    users = User.query.all()
    print("Users:\n")
    for user in users:
        print(f"id:{user.id}, name:{user.name}, email:{user.email}, phone_number:{user.phone_number}, "
              f"events:{user.events}")
    print("\n")
    # Populating random.randint() amount of events with fake data

    for _ in range(event_amount):
        event = Event(name=fake.color_name(), location=fake.street_name(), time="2025-03-15 10:00:00",
                      description=fake.catch_phrase(), organizer=fake.name())
        db.session.add(event)
    db.session.commit()
    events = Event.query.all()
    # Populating the events randomly
    print("Events:\n")
    for event in events:
        print(f"id:{event.id}, location:{event.location}, time:{event.time}, description:{event.description}, "
              f"organizer:{event.organizer}")
    print("\n")
    for event in events:
        print("Populating event participants table")
        selected_users = random.sample(users, min(random.randint(2, 15), len(users)))
        print(f"Randomly selected amount of users: {len(selected_users)}")
        for selected_user in selected_users:
            participant = EventParticipants(user_id=selected_user.id, event_id=event.id)
            db.session.add(participant)
        db.session.commit()

    # Check all participants and events
    event_participations = EventParticipants.query.all()
    for p in event_participations:
        print(f"Event {p.event_id}: User {p.user_id} ")


def create_database():
    """Creates the MySQL database with the name cfg.DB_NAME"""
    database = mysql.connector.connect(host=cfg.DB_HOST, user=cfg.DB_USERNAME, passwd=cfg.DB_PASSWORD)
    database_cursor = database.cursor()
    try:
        # database_cursor.execute(f"CREATE DATABASE {cfg.DB_NAME}")
        return database_cursor
    except mysql.connector.errors.DatabaseError as db_error:
        print(f"{db_error.__class__.__name__}:{db_error}")
        database_cursor.execute(f"DROP DATABASE {cfg.DB_NAME}")
        database_cursor.execute(f"CREATE DATABASE {cfg.DB_NAME}")
        database_cursor.execute("SHOW DATABASES")
        for databases_found in database_cursor:
            print(databases_found)
        return database_cursor


# Initialize Flask app
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (f"mysql+pymysql://{cfg.DB_USERNAME}:{cfg.DB_PASSWORD}"
                                         f"@{cfg.DB_HOST}/{cfg.DB_NAME}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)


class EventParticipants(db.Model):
    __tablename__ = "event_participants"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))


class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(128), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(2048))
    organizer = db.Column(db.String(128))
    category = db.Column(db.JSON)
    tags = db.Column(db.JSON)

    users = db.relationship("User", secondary=EventParticipants.__table__, back_populates="events")


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(128), nullable=True)

    events = db.relationship("Event", secondary=EventParticipants.__table__, back_populates="users")


if __name__ == "__main__":
    create_database()
    with app.app_context():
        db.drop_all()
        db.create_all()
        populate_database()
        users = User.query.all()
        for u in users:
            print(f"User with ID {u.id} is participating in {u.events} events")
        events = Event.query.all()
        for event in events:
            participants = [user.name for user in event.users]
            print(f"Event {event.id} ({event.name}) participants:"
                  f"{', '.join(participants) if participants else 'No participants'}")
