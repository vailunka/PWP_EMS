"""User and Event tests"""
import json as j
import pytest
import secrets
from src.resources_and_models import app, db, create_database, ApiKey
from src.db_population import populate_single_user, populate_single_event, add_user_to_event
import config as cfg


DEFAULT_JSON = {
    "name": "Shiny New Event",
    "location": "Uleåborg",
    "time": "2026-02-28T10:00:00",
    "organizer": 1,
    "description": "A very shiny new event!",
    "category": ["music", "sports"],
    "tags": ["live-music", "baby-metal-concert"]
}

SECOND_JSON = {
    "name": "Not Shiny Old Event",
    "location": "Helsingfors",
    "time": "2025-02-28T11:00:00",
    "organizer": 2
}

USER_JSON = {"name": "Test User", "email": "Test@gmail.com", "phone_number": "00584"}
JONI_MAISEMA_APIKEY = None
JONI_MAISEMA_TOKEN = None
KAYTTAJA_KAKSI_APIKEY = None
KAYTTAJA_KAKSI_TOKEN = None
ADMIN_API_TOKEN = None
ADMIN_API_KEY = None


def insert_apikey_values(joni_key, joni_token, kaksi_key, kaksi_token, admin_api_key, admin_api_token):
    global JONI_MAISEMA_APIKEY, JONI_MAISEMA_TOKEN
    global KAYTTAJA_KAKSI_APIKEY, KAYTTAJA_KAKSI_TOKEN
    global ADMIN_API_KEY, ADMIN_API_TOKEN
    JONI_MAISEMA_APIKEY = joni_key
    JONI_MAISEMA_TOKEN = joni_token
    KAYTTAJA_KAKSI_APIKEY = kaksi_key
    KAYTTAJA_KAKSI_TOKEN = kaksi_token
    ADMIN_API_KEY = admin_api_key
    ADMIN_API_TOKEN = admin_api_token

@pytest.fixture
def test_client():
    """Init Test Client"""
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
    with ctx:
        db.drop_all()
        db.create_all()
        # populate_database()
        user = populate_single_user(
            name="Joni Maisema", email="joni.maisema@gmail.com", phone_number="12345678"
        )
        user_two = populate_single_user(
            name="kayttaja kaksi",
            email="kayttajakaksi@gmail.com"
        )
        user_one_token = secrets.token_urlsafe()
        user_one_key = ApiKey(key=ApiKey.key_hash(user_one_token), user_id=user.id)
        user_two_token = secrets.token_urlsafe()
        user_two_key = ApiKey(key=ApiKey.key_hash(user_two_token), user_id=user_two.id)
        db.session.add(user_one_key)
        db.session.commit()
        db.session.add(user_two_key)
        db.session.commit()
        admin_token = secrets.token_urlsafe()
        admin_api_key = ApiKey(key=ApiKey.key_hash(admin_token), admin=True)
        db.session.add(admin_api_key)
        db.session.commit()
        # insert_apikey_values(joni_key, joni_token, kaksi_key, kaksi_token):
        insert_apikey_values(user_one_key, user_one_token, user_two_key, user_two_token, admin_api_key, admin_token)
        print(f"JONI MAISEMA: {JONI_MAISEMA_APIKEY}, KAYTTAJA KAKSI: {KAYTTAJA_KAKSI_APIKEY}")
        populate_single_event(
            name=DEFAULT_JSON["name"],
            location=DEFAULT_JSON["location"],
            organizer=DEFAULT_JSON["organizer"],
            time=DEFAULT_JSON["time"],
            description=DEFAULT_JSON["description"],
            category=DEFAULT_JSON["category"],
            event_tags=DEFAULT_JSON["tags"],
        )

        event = populate_single_event(SECOND_JSON["name"], SECOND_JSON["location"],
                                      SECOND_JSON["time"], organizer=SECOND_JSON["organizer"])
        add_user_to_event(user, event)

    yield test_client

    db.session.remove()
    db.drop_all()
    ctx.pop()


class TestEventCollection:
    """Test for Event Collection"""
    RESOURCE_URL = "/api/events/"

    def test_get(self, test_client):
        """Test for Event Collection GET"""
        response = test_client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        data = response.get_json()
        assert data
        for event in data:
            assert "name" in event
            assert "location" in event
            assert "time" in event
            assert "description" in event
            assert "category" in event
            assert "tags" in event

        # Test wrong request type
        response = test_client.post(self.RESOURCE_URL, data=DEFAULT_JSON)
        assert response.status_code == 405


class TestEventItem:
    """ Test for Event Item"""
    RESOURCE_URL = "/api/events/Shiny New Event/"
    INVALID_URL = "/api/events/sffdsadvsff/"
    MODIFIED_URL = "/api/events/WE ARE YOUNG/"
    VALID_JSON = {
        "name": "WE ARE YOUNG",
        "location": "Helsingfors",
        "time": "2025-02-28T10:00:00",
        "organizer": 1,
        "description": "A very shiny new event!",
        "category": ["music", "sports"],
        "tags": ["live-music", "baby-metal-concert"],
    }

    def test_get(self, test_client):
        """ Test for Event Item GET"""
        # Test valid
        response = test_client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        data = response.get_json()
        assert data
        assert "name" in data
        assert "location" in data
        assert "time" in data
        assert "description" in data
        assert "category" in data
        assert "tags" in data

        # Test invalid
        response = test_client.get(self.INVALID_URL)
        assert response.status_code == 404


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
        response = test_client.get(self.RESOURCE_URL, headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
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
        json = {
            "name": "Test PUT",
            "email": "TestPut@email.com",
            "phone_number": "1234567",
        }
        # Test valid
        response = test_client.put(self.RESOURCE_URL, json=json, headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
        assert response.status_code == 201

        # NOTE: from hereon, the only valid url is /api/users/Test PUT/

        # Test wrong url
        response = test_client.put(self.INVALID_URL, json=json, headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
        assert response.status_code == 404

        # Test wrong content
        response = test_client.put("/api/users/Test PUT/", data=json, headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
        assert response.status_code == 415
        # Test missing field
        json.pop("email")
        response = test_client.put("/api/users/Test PUT/", json=json, headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
        assert response.status_code == 400

    def test_delete(self, test_client):
        """Test for UserItem DELETE"""
        response = test_client.delete(self.RESOURCE_URL, headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
        assert response.status_code == 204

        response = test_client.get(self.RESOURCE_URL, headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
        assert response.status_code == 404

        response = test_client.delete(self.INVALID_URL, headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
        assert response.status_code == 404


class TestUserCollection:
    """Tests For UserCollection"""

    RESOURCE_URL = "/api/users/"

    def test_get(self, test_client):
        """Tests For UserCollection GET"""
        response = test_client.get(self.RESOURCE_URL, headers={"EMS-Api-Key": ADMIN_API_TOKEN})
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
        # data = response.get_json()
        # assert data
        # assert data["name"] == "Test Post"
        # assert data["email"] == "TestPost@email.com"
        # assert data["phone_number"] == "1234567"
        data = response.headers
        assert data["location"] == "/api/users/Test%20Post/"  # NOTE: %20 == " "

        # Testing missing field
        json.pop("email")
        response = test_client.post(self.RESOURCE_URL, json=json)
        assert response.status_code == 400


class TestUserEvents:
    """Test for UserEvents resource"""

    RESOURCE_URL = "/api/users/Joni Maisema/events/"

    def test_get(self, test_client):
        """Test for UserEvents Resource"""
        response = test_client.get(self.RESOURCE_URL, headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
        assert response.status_code == 200

        data = response.get_json()
        assert "user_name" in data
        assert data["user_name"] == "Joni Maisema"

        assert "event_infos" in data
        event_infos = data["event_infos"]
        assert "attended_events" in event_infos
        assert "organized_events" in event_infos
        assert (
            len(event_infos["attended_events"]) == 1
        )  # One attended event for the user

        attended_event = event_infos["attended_events"][0]
        assert "name" in attended_event
        assert attended_event["name"] == "Not Shiny Old Event"
        assert "location" in attended_event
        assert attended_event["location"] == "Helsingfors"
        assert "time" in attended_event
        assert attended_event["time"] == "2025-02-28T11:00:00"

        assert (
            len(event_infos["organized_events"]) == 1
        )  # Assuming the user has organized one event

        organized_event = event_infos["organized_events"][0]
        assert "name" in organized_event
        assert organized_event["name"] == "Shiny New Event"
        assert "location" in organized_event
        assert organized_event["location"] == "Uleåborg"
        assert "time" in organized_event
        assert organized_event["time"] == "2026-02-28T10:00:00"

    def test_post(self, test_client):
        """Test for Event Collection POST"""
        json = DEFAULT_JSON.copy()
        json.pop("organizer")

        # Test invalid
        response = test_client.post(self.RESOURCE_URL, data=json, headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
        assert response.status_code == 415

        # Test valid
        response = test_client.post(self.RESOURCE_URL, json=json, headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
        assert response.status_code == 201
        data = response.headers
        # print(f"DATA IS: {data}")
        # assert data
        # assert data["name"] == "Shiny New Event"
        # assert data["location"] == "Uleåborg"
        # assert data["time"] == "2026-02-28T10:00:00"
        # assert data["organizer"] == 1
        # assert data["description"] == "A very shiny new event!"
        # assert data["category"] == ["music", "sports"]
        # assert data["tags"] == ["live-music", "baby-metal-concert"]
        print(f"DATA LOCATION: {data['location']}")
        assert data["location"] == f"/api/events/Shiny%20New%20Event/"

        # Test same
        # response = test_client.post(self.RESOURCE_URL, json=json)
        # assert response.status_code == 409

        # Test missing field
        json.pop("location")
        response = test_client.post(self.RESOURCE_URL, json=json, headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
        assert response.status_code == 400


class TestUserEventItem:
    """Test for UserEventItem resource"""

    RESOURCE_URL = "/api/users/Joni Maisema/events/Shiny New Event/"
    INVALID_URL = "/api/users/Joni Maisema/events/sffdsadvsff/"
    MODIFIED_URL = "/api/events/WE ARE YOUNG/"
    VALID_JSON = {
        "name": "WE ARE YOUNG",
        "location": "Helsingfors",
        "time": "2025-02-28T10:00:00",
        "organizer": 1,
        "description": "A very shiny new event!",
        "category": ["music", "sports"],
        "tags": ["live-music", "baby-metal-concert"],
    }

    def test_put(self, test_client):
        """ Test for Event Item PUT"""
        json = DEFAULT_JSON.copy()
        # Test wrong content type
        response = test_client.put(self.RESOURCE_URL, data=json, headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
        assert response.status_code == 415

        # Test invalid url
        response = test_client.put(self.INVALID_URL, json=json, headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
        assert response.status_code == 404

        # Test different events name
        # json["name"] = "Cool consert"
        # response = test_client.put(self.RESOURCE_URL, json=json)
        # assert response.status_code == 409

        # Test valid
        json["name"] = DEFAULT_JSON["name"]
        response = test_client.put(self.RESOURCE_URL, json=json, headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
        assert response.status_code == 200

        # Test missing field
        json.pop("location")
        response = test_client.put(self.RESOURCE_URL, json=json, headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
        assert response.status_code == 400

        # Test URL  modification
        json = self.VALID_JSON
        test_client.put(self.RESOURCE_URL, json=json, headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
        response = test_client.get(self.MODIFIED_URL,)
        assert response.status_code == 200
        resp_body = j.loads(response.data)
        assert resp_body["location"] == json["location"]

    def test_delete(self, test_client):
        """ Test for Event Item DELETE"""
        # Test item deletion
        response = test_client.delete(self.RESOURCE_URL, headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
        assert response.status_code == 204

        # See that it got deleted
        response = test_client.get(f"/api/events/Shiny New Event/", headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
        assert response.status_code == 404

        # Test invalid deletion
        response = test_client.delete(self.INVALID_URL, headers={"User-Api-Key": JONI_MAISEMA_TOKEN})
        assert response.status_code == 404
