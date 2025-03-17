"""This is test file for user related resoures"""

import pytest

from db_implementation import app, db, create_database
from db_population import populate_single_user, populate_single_event
import config as cfg

DEFAULT_JSON = {
    "name": "Shiny New Event",
    "location": "Uleåborg",
    "time": "2025-02-28 10:00:00",
    "organizer": 1,
    "description": "A very shiny new event!",
    "category": ["music", "sports"],
    "tags": ["live-music", "baby-metal-concert"],
}

USER_JSON = {"name": "Test User", "email": "Test@gmail.com", "phone_number": "00584"}


@pytest.fixture
def test_client():
    """Initialize test client"""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{cfg.DB_USERNAME}:{cfg.DB_PASSWORD}"
        f"@{cfg.DB_HOST}/{cfg.DB_NAME}"
    )

    client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    create_database()
    with ctx:
        db.drop_all()
        db.create_all()
        # populate_database()
        populate_single_user(
            name="Joni Maisema", email="joni.maisema@gmail.com", phone_number="12345678"
        )
        populate_single_user(
            name="kayttaja kaksi",
            email="kayttajakaksi@gmail.com",
            phone_number="00000000",
        )
        populate_single_event(
            name=DEFAULT_JSON["name"],
            location=DEFAULT_JSON["location"],
            time=DEFAULT_JSON["time"],
            organizer=DEFAULT_JSON["organizer"],
            description=DEFAULT_JSON["description"],
            category=DEFAULT_JSON["category"],
            event_tags=DEFAULT_JSON["tags"],
        )

    yield client

    db.session.remove()
    db.drop_all()
    ctx.pop()


class TestUserItem:
    """Test for Resource UserItem"""

    RESOURCE_URL = "/api/users/Joni Maisema/"
    RESOURCE_URL1 = "/api/users/kayttaja kaksi/"
    INVALID_URL = "/api/users/adadfasa/"
    MODIFIED_URL = "/api/users/TestUser2/"
    VALID_JSON = {
        "name": "TestUser2",
        "email": "Test2@gmail.com",
        "phone_number": "05844555",
    }

    def test_get(self, test_client):
        """Test for UserItem GET"""
        # Test valid
        response = test_client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        data = response.get_json()
        assert data
        assert "name" in data
        assert "email" in data
        assert "phone_number" in data

        # Test invalid url
        response = test_client.get(self.INVALID_URL)
        assert response.status_code == 404

    def test_put(self, test_client):
        """Test for UserItem PUT"""
        json = USER_JSON.copy()
        # Test wrong content
        response = test_client.put(self.RESOURCE_URL, data=json)
        assert response.status_code == 415

        # Test wrong url
        response = test_client.put(self.INVALID_URL, json=json)
        assert response.status_code == 404

        # Test valid
        response = test_client.put(self.RESOURCE_URL, json=json)
        assert response.status_code == 201

        # Test missing field
        json.pop("email")
        response = test_client.put(self.RESOURCE_URL, json=json)
        assert response.status_code == 404

        # Test URL modification

        # json1 = self.VALID_JSON.copy()
        # response = test_client.put(self.RESOURCE_URL, json=json1)
        # assert response.status_code == 201

        # response = test_client.get(self.MODIFIED_URL)
        # assert response.status_code == 200
        # resp_body = j.loads(response.data)
        # assert resp_body["email"] == json["email"]

    def test_delete(self, test_client):
        """Test for UserItem DELETE"""
        response = test_client.delete(self.RESOURCE_URL)
        assert response.status_code == 204

        response = test_client.get(self.RESOURCE_URL)
        assert response.status_code == 404

        response = test_client.delete(self.INVALID_URL)
        assert response.status_code == 404


class TestUserCollection:
    """Tests For UserCollection"""

    RESOURCE_URL = "/api/users/"

    def test_get(self, test_client):
        """Tests For UserCollection GET"""
        response = test_client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        data = response.get_json()
        assert data
        for user in data:
            assert "name" in user
            assert "email" in user
            assert "phone_number" in user

    def test_post(self, test_client):
        """Tests For UserCollection POST"""
        json = {
            "name": "Test Post",
            "email": "TestPost@email.com",
            "phone_number": "1234567",
        }

        # Test invalid
        response = test_client.post(self.RESOURCE_URL, data=json)
        assert response.status_code == 415

        # Test valid
        response = test_client.post(self.RESOURCE_URL, json=json)
        assert response.status_code == 201
        data = response.get_json()
        assert data
        assert data["name"] == "Test Post"
        assert data["email"] == "TestPost@email.com"
        assert data["phone_number"] == "1234567"

        # Testing missing field
        json.pop("email")
        response = test_client.post(self.RESOURCE_URL, json=json)
        assert response.status_code == 400


class TestUserEvents:
    """Test for UserEvents resource"""

    RESOURCE_URL = "/api/users/Joni Maisema/events/"

    def test_get(self, test_client):
        """Test for UserEvents Resource"""
        response = test_client.get(self.RESOURCE_URL)
        assert response.status_code == 200

        data = response.get_json()
        assert "user_name" in data
        assert data["user_name"] == "Joni Maisema"

        assert "event_infos" in data
        event_infos = data["event_infos"]
        assert "attended_events" in event_infos
        assert "organized_events" in event_infos
        assert (
            len(event_infos["attended_events"]) == 0
        )  # No attended events for the user
        assert (
            len(event_infos["organized_events"]) == 1
        )  # Assuming the user has organized one event

        organized_event = event_infos["organized_events"][0]
        assert "name" in organized_event
        assert organized_event["name"] == "Shiny New Event"
        assert "location" in organized_event
        assert organized_event["location"] == "Uleåborg"
        assert "time" in organized_event
        assert organized_event["time"] == "2025-02-28 10:00:00"
