import requests
import keyring
from datetime import datetime, timedelta
import json


class EMSClient:

    def __init__(self, base_url):
        self.BASE_URL = base_url  # most likely http://127.0.0.1:5000/api/
        self.api_key = None
        self.current_user = None
        self.admin_key = None

    def load_admin_key(self):
        """Load admin key from secure storage, acts as 'admin login' """
        self.set_admin_key()

    def set_admin_key(self, key=None):
        """
        Set the admin API key
        If no key provided, tries to load from keyring
        """
        if key is not None:
            self.admin_key = key
        else:
            try:
                self.admin_key = keyring.get_password("EMS_admin", "admin")
                if not self.admin_key:
                    raise ValueError("No admin key found in keyring")
            except Exception as e:
                raise ValueError(f"Failed to access keyring: {str(e)}")

    def admin_request(self, method, endpoint, **kwargs):
        """Make authenticated admin request"""
        if not self.admin_key:
            raise ValueError("Admin API key not available")

        headers = kwargs.get('headers', {})
        headers['EMS-Api-Key'] = self.admin_key
        kwargs['headers'] = headers

        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(method, url, timeout=10, **kwargs)

        if response.status_code == 403:
            print("Invalid or expired admin API key")
            self.admin_key = None

        return response

    def authenticated_request(self, method, endpoint, **kwargs):
        """
        Makes authenticated request and handles API key logic.

        :param str method: HTTP method to be used (GET, PUT, POST, DELETE)
        :param str endpoint: Endpoint of the request (excluding the BASE_URL part)
        :param kwargs: Additional parameters
        :returns obj: Response object
        """
        if not self.api_key:
            raise ValueError("API key not available")

        # Fixed the method validation
        if method.upper() not in ["GET", "PUT", "POST", "DELETE"]:
            raise ValueError(f"{method} is not an implemented method, "
                             f"accepted values are GET, PUT, POST and DELETE")

        headers = kwargs.get('headers', {})
        headers['User-Api-Key'] = self.api_key
        kwargs['headers'] = headers
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(method, url, timeout=10, **kwargs)

        if response.status_code == 403:
            print(f"[{method}] Invalid API key")
            self.api_key = None
            self.current_user = None

        return response

    # User related methods
    def create_user(self, username, email, phone_number=""):
        """
        Creates a user via POST request.

        :param str username: Name of the user
        :param str email: Email of the user
        :param str phone_number: (Optional) Phone number of the user
        :returns bool: Returns True if user creation was successful, False otherwise
        """
        print(f"Creating user")
        url = f"{self.BASE_URL}users/"
        contents = {"name": username, "email": email}
        if phone_number:
            contents["phone_number"] = phone_number
        response = requests.post(url=url, json=contents, timeout=10)

        if response.status_code == 201:
            api_key = response.headers.get("User-Api-Key")
            if api_key:
                keyring.set_password("EMS_user", username, api_key)
                self.api_key = api_key
                self.current_user = username
                print(f"User {username} created successfully.")
                return True
        print(f"Error in creating user: {response.status_code}, {response.text}")
        return False

    def user_login(self, username):
        """
        Log in as user

        :param str username: Name of the user
        :return bool: True if login was successful, False otherwise
        """
        if not username:
            print("Username was not given")
            return False
        user_key = keyring.get_password("EMS_user", username)
        if not user_key:
            print("User does not exist")
            return False
        if user_key == self.api_key and self.current_user == username:
            print(f"Already logged in as {self.current_user}")
            return False
        else:
            self.current_user = username
            self.api_key = user_key
            print("Logged in successfully")
            return True

    def user_logout(self, username):
        if not username:
            print("Username was not given")
            return False

        self.current_user = None
        self.api_key = None

    def get_user(self):
        """
        GETs all the information about the user.

        :returns dictionary/None: User information as a dictionary or None
        """
        if not self.current_user:
            print("User is none - cannot make GET request. Please log in or create a user first")

        endpoint = f"users/{self.current_user}/"
        response = self.authenticated_request("GET", endpoint)
        if response.status_code == 200:
            return response.json()
        return

    def modify_user(self, modified_contents):
        """
        Modifies the user via PUT request.

        :param dict modified_contents: Modified contents of the user

        :returns bool: True if modification was successful, False otherwise
        """
        if not self.current_user:
            print("User is none - cannot make PUT request. Please log in or create a user first")
            return False

        endpoint = f"users/{self.current_user}/"
        response = self.authenticated_request("PUT", endpoint=endpoint, json=modified_contents)

        if response.status_code == 201:
            old_username = self.current_user
            new_username = modified_contents['name']

            if old_username != new_username:
                api_key = keyring.get_password("EMS_user", old_username)
                if api_key:
                    keyring.set_password("EMS_user", new_username, api_key)
                    keyring.delete_password("EMS_user", old_username)

            self.current_user = new_username
            print(f"User {new_username} modified successfully.")
            return True

        return False


    def delete_user(self):
        """
        Deletes the current user via DELETE request.

        :returns bool: True if deletion was successful, False otherwise
        """
        if not self.current_user:
            print("User is none - cannot make DELETE request. Please log in or create a user first")
            return False

        endpoint = f"users/{self.current_user}/"
        response = self.authenticated_request("DELETE", endpoint=endpoint)
        if response.status_code == 204:
            print(f"User {self.current_user} was deleted successfully.")

            try:
                keyring.delete_password("EMS_user", self.current_user)
            except keyring.errors.PasswordDeleteError:
                print("Keyring entry not found or already deleted.")

            self.current_user = None
            self.api_key = None
            return True

        return False

    def get_user_events(self):
        """
        GETs the events user has attended and/or organized.

        :return dict: Dictionary of user related events
        """

        if not self.current_user:
            print("User is none - cannot make DELETE request. Please log in or create a user first")
        endpoint = f"users/{self.current_user}/events/"
        response = self.authenticated_request("GET", endpoint=endpoint)
        if response.status_code == 200:
            print(f"Got user related events successfully")
            return response.json()
        return

    def get_all_users(self):
        """Admin-only: Get list of all users"""
        response = self.admin_request("GET", "users/")
        print(f"response is: {response.json()}")
        return response.json() if response.status_code == 200 else None

    def create_event(self, name, location, time, description, category=None, tags=None):
        """
        Creates an event with given parameters. organizer id is handled on the server side

        :param str name: Name of the event
        :param str location: Location of the event
        :param datetime time: Time of the event
        :param str description: Description of the event
        :param list category: (Optional) List of categories that the event belongs to
        :param list tags: (Optional) List of the tags that event has

        :returns bool: True if event creation was successful, False otherwise
        """
        if not self.current_user:
            print("User is none - cannot make POST request. Please log in or create a user first")

        endpoint = f"users/{self.current_user}/events/"

        event_details = {"name": name, "location": location, "time": time.isoformat(), "description": description}
        if category:
            event_details["category"] = category
        if tags:
            event_details["tags"] = tags

        response = self.authenticated_request("POST", endpoint=endpoint, json=event_details)
        if response.status_code == 201:
            print(f"Event created successfully.")
            return True
        return False

    def get_event(self, name):
        """
        GETs information about an event.

        :param str name: Name of the event

        :returns dict/None: Dictionary of the event details or None
        """

        endpoint = f"events/{name}/"
        response = requests.get(f"{self.BASE_URL}{endpoint}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return

    def modify_event(self, name, location, time, description, category=None, tags=None):
        """
        Modifies an event with given parameters. organizer id is handled on the server side

        :param str name: Name of the event
        :param str location: Location of the event
        :param datetime time: Time of the event
        :param str description: Description of the event
        :param list category: (Optional) List of categories that the event belongs to
        :param list tags: (Optional) List of the tags that event has

        :returns bool: True if event creation was successful, False otherwise
        """
        if not self.current_user:
            print("User is none - cannot make PUT request. Please log in or create a user first")

        endpoint = f"users/{self.current_user}/events/{name}/"

        event_details = {"name": name, "location": location, "time": time, "description": description}
        if category:
            event_details["category"] = category
        if tags:
            event_details["tags"] = tags

        response = self.authenticated_request("PUT", endpoint=endpoint)
        if response.status_code == 201:
            print(f"Event created successfully.")
            return True
        return False

    def delete_event(self, name):
        """
        Deletes an event

        :param str name: Name of the event
        :return bool: True if deletion was successful, otherwise false
        """
        endpoint = f"users/{self.current_user}/events/{name}/"
        response = self.authenticated_request("DELETE", endpoint=endpoint)
        if response.status_code == 204:
            print("Event deleted successfully.")
            return True
        return False

    def get_events(self):
        """
        Gets all events

        :returns dict/None: Dictionary of all the events or None
        """
        endpoint = f"events/"
        response = requests.get(f"{self.BASE_URL}{endpoint}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return

    def add_user_as_participant(self, event):
        """
        Adds user as participant to an event.

        :param str event: Name of the event
        :returns bool: True if adding user to participants was successful, False otherwise
        """
        endpoint = f"events/{event}/participants/{self.current_user}/"
        if not self.current_user:
            print("User is none - cannot make POST request. Please log in or create a user first")
        response = self.authenticated_request("POST", endpoint=endpoint)
        if response.status_code == 201:
            print(f"User {self.current_user} added as participant to the event {event}.")
            return True
        return False

    def remove_user_participation(self, event):
        """
        Removes user from event participants.

        :param str event: Name of the event
        :returns bool: True if deleting user from participants was successful, False otherwise
        """
        endpoint = f"events/{event}/participants/{self.current_user}/"
        if not self.current_user:
            print("User is none - cannot make DELETE request. Please log in or create a user first")
        response = self.authenticated_request("DELETE", endpoint=endpoint)
        if response.status_code == 204:
            print(f"User {self.current_user} deleted from participants @ event: {event}.")
            return True
        return False


if __name__ == "__main__":
    c = EMSClient("http://127.0.0.1:5000/api/")
    #c2 = EMSClient("http://127.0.0.1:5000/api/")
    #c3 = EMSClient("http://127.0.0.1:5000/api/")
    c.load_admin_key()
    print(f"current user: {c.current_user}")
    c.create_user("aaa", "bbb", "ccc")
    print(f"current user: {c.current_user}")
    #c2.create_user("asdasd", "qwdasdas", "adssadasa")
    print(f"current user: {c.current_user}")
    c.get_all_users()
    #c.get_all_users()
    c.create_event("testi", "testi", datetime.now() + timedelta(hours=1), "testi", ["nope"], ["nops"])
    c.create_event("testikakkonen", "testikakkonen", datetime.now() + timedelta(hours=5), "testikakkonen")
    s_ek = c.get_event("testikakkonen")
    ev = c.get_user_events()
    print(json.dumps(ev))
    c.create_user("moi", "hei", "terve")
    c.add_user_as_participant("testi")
    c.add_user_as_participant("testikakkonen")
    ev = c.get_user_events()
    print(json.dumps(ev))
    c.remove_user_participation("testikakkonen")
    ev = c.get_user_events()
    print(json.dumps(ev))
    c.delete_event("testikakkonen")
