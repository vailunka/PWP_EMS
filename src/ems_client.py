import requests
import keyring


class EMSClient:

    def __init__(self, base_url):
        self.BASE_URL = base_url  # most likely http://127.0.0.1:5000/api/
        self.api_key = None
        self.current_user = None

    def authenticated_request(self, method, endpoint, **kwargs):
        """
        Makes authenticated request and handles API key logic.

        :param str method: HTTP method to be used (GET, PUT, POST, DELETE)
        :param str endpoint: Endpoint of the request (excluding the BASE_URL part)
        :param kwargs: Additional parameters
        :return:
        """
        if not self.api_key:
            raise ValueError("API key not available")
        if any(["GET", "PUT", "POST", "DELETE"]) not in method:
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
                # keyring.set_password("EMS_user", username, api_key)
                self.api_key = api_key
                self.current_user = username
                print(f"User {username} created successfully.")
                return True
        print(f"Error in creating user: {response.status_code}, {response.text}")
        return False

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
        endpoint = f"users/{self.current_user}/"
        response = self.authenticated_request("PUT", endpoint=endpoint, json=modified_contents)
        if response.status_code == 201:
            print(f"User {modified_contents['name']} modified successfully.")
            self.current_user = modified_contents['name']
            return True
        return False

    def delete_user(self):
        """
        Deletes the current user via DELETE request.

        :returns bool: True if deletion was successful, False otherwise
        """

        if not self.current_user:
            print("User is none - cannot make DELETE request. Please log in or create a user first")
        endpoint = f"users/{self.current_user}/"
        response = self.authenticated_request("DELETE", endpoint=endpoint)
        if response.status_code == 204:
            print(f"User {self.current_user} was deleted successfully.")
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

    # TODO --> admin-logiikka tätä varten
    def get_all_users(self):
        pass

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

        event_details = {"name": name, "location": location, "time": time, "description": description}
        if category:
            event_details["category"] = category
        if tags:
            event_details["tags"] = tags

        response = self.authenticated_request("POST", endpoint=endpoint)
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
