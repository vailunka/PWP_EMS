# PWP SPRING 2025
# Event Management System
# Group information
* Student 1. Ville Ailunka, Ville.Ailunka@student.oulu.fi
* Student 2. Tommi Jokinen, Tommi.Jokinen@student.oulu.fi
* Student 3. Joni Kemppainen, Joni.E.Kemppainen@student.oulu.fi
* Student 4. Jere Jacklin, Jere.Jacklin@student.oulu.fi

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint, instructions on how to setup and run the client, instructions on how to setup and run the axiliary service and instructions on how to deploy the api in a production environment__

### Creating and populating the database
All the required packages can be installed in the python virtual environment by running the following command: `pip install -r path/to/requirements.txt`.
Our database utilizes MySQL.

The database implementation can be found from the `db_implementation.py` file. We created a random database population script that will create and populate the database with random data utilizing the [Faker Python package](https://faker.readthedocs.io/en/master/). The database can be populated simply by running `python db_population.py` in the Python virtual environment.

Tutorial for MySQL usage: 
https://www.youtube.com/watch?v=3vsC05rxZ8c&t=533s&ab_channel=TechWithTim

MySQL version = 8.0.41

30.1.2025: In the database implementation we decided to go with MySQL used via SQLAlchemy because it is well suitable for general purpose web applications.
