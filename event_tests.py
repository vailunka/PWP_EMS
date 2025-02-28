import pytest
from datetime import datetime

from db_implementation import app, db, create_database
from db_population import populate_database
import config as cfg
import json as j

@pytest.fixture
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = (f"mysql+pymysql://{cfg.DB_USERNAME}:{cfg.DB_PASSWORD}"
                                             f"@{cfg.DB_HOST}/{cfg.DB_NAME}")

    test_client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    create_database()
    with ctx:
        db.drop_all()
        db.create_all()
        populate_database()

    yield test_client

    db.session.remove()
    db.drop_all()
    ctx.pop()


class TestEventCollection(object):
    RESOURCE_URL = "/api/events/"

    def test_get(self,test_client):
        response = test_client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        data = response.get_json()
        for event in data:
            assert "name" in event
            assert "location" in event
            assert "time" in event
            assert "description" in event
            assert "category" in event
            assert "tags" in event

    def test_post(self, test_client):
        json = {
            "name": "Shiny New Event",
            "location": "Uleåborg",
            "time": "2025-02-28 10:00:00",
            "organizer": 1,
            "description": "A very shiny new event!",
            "category": ["music", "sports"],
            "tags": ["live-music", "baby-metal-concert"]
        }

        # Test invalid
        response = test_client.post(self.RESOURCE_URL, data={})
        assert response.status_code == 415


        # Test valid
        response = test_client.post(self.RESOURCE_URL, json=json)
        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "Shiny New Event"
        assert data["location"] == "Uleåborg"
        assert data["time"] == "2025-02-28 10:00:00"
        assert data["organizer"] == 1
        assert data["description"] == "A very shiny new event!"
        assert data["category"] == ["music", "sports"]
        assert data["tags"] == ["live-music", "baby-metal-concert"]

        # Test same
        response = test_client.post(self.RESOURCE_URL, json=json)
        assert response.status_code == 409

        # Test missing field
        json.pop("location")
        response = test_client.post(self.RESOURCE_URL, json=json)
        assert response.status_code == 400




class TestEventItem(object):
    RESOURCE_URL = "/api/events/test-event"
    INVALID_URL = "/api/events/sffdsadvsff"
    MODIFIED_URL = "/api/events/different-event"
    VALID_JSON = {
            "name": "Shiny New Event",
            "location": "Uleåborg",
            "time": "2025-02-28 10:00:00",
            "organizer": 1,
            "description": "A very shiny new event!",
            "category": ["music", "sports"],
            "tags": ["live-music", "baby-metal-concert"]
        }

    def test_get(self, test_client):

        # Test valid
        response = test_client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        data = response.get_json()
        assert "name" in data
        assert "location" in data
        assert "time" in data
        assert "description" in data
        assert "category" in data
        assert "tags" in data

        # Test invalid
        response = test_client.get(self.INVALID_URL)
        assert response.status_code == 404

    def test_put(self, test_client):
        json = self.VALID_JSON.copy()
        # Test wrong content type
        response = test_client.put(self.RESOURCE_URL, data=json)
        assert response.status_code == 415

        # Test invalid url
        response = test_client.put(self.INVALID_URL, json=json)
        assert response.status_code == 404

        # Test different events name
        json["name"] = "Cool consert" # TODO: This name should be already in the database when populated
        response = test_client.put(self.RESOURCE_URL, json=json)
        assert response.status_code == 409

        # Test valid
        json["name"] = "Test event"
        response = test_client.put(self.RESOURCE_URL, json=json)
        assert response.status_code == 204

        # Test missing field
        json.pop("location")
        response = test_client.put(self.RESOURCE_URL, json=json)
        assert response.status_code == 400

        # Test URL  modification
        json = self.VALID_JSON
        response = test_client.put(self.RESOURCE_URL, json=json)
        response = test_client.get(self.MODIFIED_URL)
        assert response.status_code == 200
        resp_body = j.loads(response.data)
        assert resp_body["location"] == json["location"]

    def test_delete(self, test_client):

        # Test item deletion
        response = test_client.delete(self.RESOURCE_URL)
        assert response.status_code == 204

        # See that it got deleted
        response = test_client.get(self.RESOURCE_URL)
        assert response.status_code == 404

        # Test invalid deletion
        response = test_client.delete(self.INVALID_URL)
        assert response.status_code == 404



