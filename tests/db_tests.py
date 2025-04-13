import pytest
from flask import Flask
from datetime import datetime

from src.resources_and_models import db, Event, User, create_database
import config as cfg


@pytest.fixture
def test_client():
    # Create application and db for testing, clean up after
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{cfg.DB_USERNAME}:{cfg.DB_PASSWORD}"
        f"@{cfg.DB_HOST}/{cfg.DB_NAME}"
    )
    test_client = app.test_client()
    ctx = app.app_context()
    ctx.push()

    create_database()
    db.init_app(app)
    db.create_all()

    yield test_client

    db.session.remove()
    db.drop_all()
    ctx.pop()


@pytest.fixture
def database_init(test_client):
    # Add a value to User
    user = User(
        name="Joni Maisema", email="joni.maisema@gmail.com", phone_number="12345678"
    )
    db.session.add(user)

    # Add a value to Event
    event = Event(
        name="Testing Event",
        location="Testing Location",
        time="2025-2-28 15:00:00",
        organizer=user.id,
        description="Lorem ipsum...",
        category="Testing Category",
        tags="testing, tech",
    )

    db.session.add(event)
    db.session.commit()

    yield

    db.session.query(User).delete()
    db.session.query(Event).delete()
    db.session.commit()


def test_user_creation(test_client, database_init):
    user = User.query.filter_by(name="Joni Maisema").first()
    assert user.name == "Joni Maisema"
    assert user.email == "joni.maisema@gmail.com"
    assert user.phone_number == "12345678"


def test_event_creation(database_init):
    user = User.query.filter_by(name="Joni Maisema").first()
    event = Event.query.filter_by(name="Testing Event").first()

    assert event.name == "Testing Event"
    assert event.location == "Testing Location"
    # Compare datetime.datetime objects
    assert event.time == datetime(2025, 2, 28, 15, 0)
    assert event.description == "Lorem ipsum..."
    assert event.category == "Testing Category"
    assert event.tags == "testing, tech"
    assert event.organizer == user.id
    assert event.description == "Lorem ipsum..."
    assert event.category == "Testing Category"
    assert event.tags == "testing, tech"


def test_user_event_relationship(test_client, database_init):
    user = User.query.filter_by(name="Joni Maisema").first()
    event = Event.query.filter_by(name="Testing Event").first()
    assert event.id in user.attended_events
    assert user.id in event.organizer


def test_update_event(test_client, database_init):
    event = Event.query.filter_by(name="Testing Event").first()
    event.description = "Lorem ipsum trallallalaa"
    db.session.commit()
    updated_event = Event.query.filter_by(name="Testing Event").first()
    assert updated_event.description == "Lorem ipsum trallallalaa"


def test_update_user(test_client, database_init):
    user = User.query.filter_by(name="Joni Maisema").first()
    user.phone_number = "987654321"
    db.session.commit()
    updated_user = User.query.filter_by(name="Joni Maisema").first()
    assert updated_user.phone_number == "987654321"


def test_delete_event(test_client, database_init):
    event = Event.query.filter_by(name="Testing Event").first()
    db.session.delete(event)
    db.session.commit()
    deleted_event = Event.query.filter_by(name="Testing Event").first()
    assert deleted_event is None
    user = User.query.filter_by(name="Joni Maisema").first()
    assert event.id not in user.attended_events


def test_delete_user(test_client, database_init):
    user = User.query.filter_by(name="Joni Maisema").first()
    db.session.delete(user)
    db.session.commit()
    deleted_user = User.query.filter_by(name="Joni Maisema").first()
    assert deleted_user is None
    event = Event.query.filter_by(name="Testing Event").first()
    assert event.organizer is None
