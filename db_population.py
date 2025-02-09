import random
from faker import Faker
from db_implementation import db, app, User, Event, EventParticipants
import config as cfg
import mysql.connector

fake = Faker()


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


def populate_database():
    """Populates the database with random amount of data (utilizing faker to generate fake data)"""
    user_amount = random.randint(5, 50)
    event_amount = random.randint(3, 10)
    print(f"Amount of users: {user_amount}\nAmount of events: {event_amount}\n")
    # Populating random.randint() amount of users with fake data
    for _ in range(user_amount):
        user = User(name=fake.name(), email=fake.email(), phone_number=fake.phone_number())
        db.session.add(user)
    db.session.commit()
    users_query = User.query.all()
    print("Users:")
    for user in users_query:
        print(f"id:{user.id}, name:{user.name}, email:{user.email}, phone_number:{user.phone_number}, "
              f"events:{user.events}")
    # Populating random.randint() amount of events with fake data
    for _ in range(event_amount):
        event_to_add = Event(name=fake.color_name(), location=fake.street_name(), time="2025-03-15 10:00:00",
                             description=fake.catch_phrase(), organizer=fake.name())
        db.session.add(event_to_add)
    db.session.commit()
    events_query = Event.query.all()
    # Populating the events randomly
    print("\nEvents:")
    for event_info in events_query:
        print(f"id:{event_info.id}, location:{event_info.location}, time:{event_info.time},"
              f"description:{event_info.description}, organizer:{event_info.organizer}")
    print("\nPopulating event participants table")
    for event in events_query:
        selected_users = random.sample(users_query, min(random.randint(2, 15), len(users_query)))
        print(f"Randomly selected amount of users: {len(selected_users)}")
        for selected_user in selected_users:
            participant = EventParticipants(user_id=selected_user.id, event_id=event.id)
            db.session.add(participant)
        db.session.commit()

    # These can be uncommented to see the EventParticipant information line by line
    # event_participations = EventParticipants.query.all()
    # print("\nEvent participation prints:")
    # for p in event_participations:
        # print(f"Event {p.event_id}: User {p.user_id} ")


if __name__ == "__main__":
    create_database()
    with app.app_context():
        db.drop_all()
        db.create_all()
        populate_database()
        users = User.query.all()
        print("\nUser-wise event information:")
        for u in users:
            print(f"User with ID {u.id} is participating in {u.events} events")
        print("\nEvent-wise participant information:")
        events = Event.query.all()
        for e in events:
            participants = [user.name for user in e.users]
            print(f"Event {e.id} ({e.name}) participants:"
                  f"{', '.join(participants) if participants else 'No participants'}")