import requests
import keyring


class EMSClient:

    def __init__(self, base_url):
        self.base_url = base_url
        self.api_key = None
        self.current_user = None

    def create_user(self, username, email, phone_number=""):
        """
        Creates a user.

        :return bool: Returns True if user creation was successful, False otherwise
        """
        print(f"Creating user")
        url = f"{self.base_url}/users/"
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

    # TODO --> pitää jotenkin luoda admin-käyttäjä ja kattoa oikat sille ymstmsjne