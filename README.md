# PWP SPRING 2025
# Event Management System
# Group information
* Student 1. Ville Ailunka, Ville.Ailunka@student.oulu.fi
* Student 2. Tommi Jokinen, Tommi.Jokinen@student.oulu.fi
* Student 3. Joni Kemppainen, Joni.E.Kemppainen@student.oulu.fi
* Student 4. Jere Jacklin, Jere.Jacklin@student.oulu.fi

## Project Structure
- **src**:
    - Contains all the functionalities of the API and also the methods to populate the database
- **tests**:
    - Contains all the scripts used to test the implementation
- **image**:
    - Contains `.png/.PNG` files for the wiki
- **python-flask-server-generated**:
    - Contains the files to run the API documentation locally
    - **NOTE: The folder also contains a `requirements.txt` file, meaning that you need to create a new virtual environment to run the documentation because of conflicting versions in the requirements.**
- **Dump20250209**:
    - Contains SQL dumps of the database
- **deployment**:
    - Contains the YAML file used in the deployment and the README for setting up the deployment.
- **repository root**:
    - Contains all the "extra" stuff such as this README, example output of populating the database etc.
    - Contains the `requirements.txt` file to run and test the API

### Creating and populating the database
#### MySQL database
Our project uses MySQL (version 8.0.41) for managing the database, meaning you will need to have MySQL running locally to be able to use the files in this repository as-is. We chose to use MySQL with SQLAlchemy because it is well suited for general purpose web applications.

Tutorial for MySQL usage: 
https://www.youtube.com/watch?v=3vsC05rxZ8c&t=533s&ab_channel=TechWithTim

After you have MySQL running locally, update the `config.py` file with your database credentials, most notably the `DB_USERNAME` and `DB_PASSWORD` values need to be correct.

#### Virtual environments
First, create a new virtual environment with: `python -m venv /path/to/venv`. After that, activate the virtual environment with the following commands depending on your operating system:
- Linux (bash/zsh): `source <venv>/bin/activate`
- Windows: `path\to\venv\Scripts\activate` or `path\to\venv\Scripts\activate.bat` or `path\to\venv\Scripts\Activate.ps1`

After that, install the packages by running `pip install -r requirements.txt` in the repository root folder. You should now have all the necessary packages installed for running the code

#### Populating the database
Currently, there are two methods of populating the database:
- Uncommenting `populate_database()` and `if "__name__" == "__main__"` sections and running the `db_population.py` file
    - The method uses the [Faker Python package](https://faker.readthedocs.io/en/master/) to create random data and populate the database with it
- Populating the database one entry at a time by using the methods below:
    - `populate_single_user()`: creates a single user with given arguments
    - `populate_single_event()`: creates a single event with given arguments
        - **NOTE: requires atleast one user to exist to create an event because the `event.organizer` requires `user.id` value**
    - `add_user_to_event()`: adds the user as a participant to the event

The latter method is used in the tests and it is **the recommended way** to make sure the database entries are correct.

### Running the tests
To test the implementation with test coverage, simply run `coverage run -m pytest ./tests/user_and_event_tests.py` from the repository root.

To see the test coverage report in the CLI, run `coverage report`. You can also generate a html report to see everything in more detail by running `coverage html`.

### Running the documentation

Documentation is ran automatically when the server hosting the API is online. The documentation can be found from `http://localhost:5000/apidocs/`

### Running the GUI / Client
The Graphical User Interface can be run by using the command: `python -m src.gui`. *The client itself can be found from* `src/ems_client.py`. 

### Deploying the application on Rahti

The application can be run by importing the deployment.yaml to Rahti. Since the MySQL IP address changes every deployment, it needs to be changed to the config.py file. After the change, the dockerfile needs to be rebuilt and pushed to the repository. Then you need to restart the application pod. Finally, you need to setup a route to the PWP EMS service in Rahti. The deployment should work now.
