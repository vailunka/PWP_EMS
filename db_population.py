"""This file is for populating"""

import random
from faker import Faker
from db_implementation import db, app, User, Event, create_database


fake = Faker()
categories = [
    "music",
    "sports",
    "festival",
    "outdoor",
    "technology",
    "education",
    "food",
    "art",
    "business",
]
tags = [
    "live-music",
    "jazz-concert",
    "indie-rock",
    "electronic-dance",
    "classical-music",
    "charity-gala",
    "fundraising-dinner",
    "outdoor-festival",
    "music-festival",
    "food-truck",
    "street-food",
    "wine-tasting",
    "gourmet-dinner",
    "cocktail-mixing",
    "cooking-class",
]


def populate_database():
    """Populates the database with random amount of data (utilizing faker to generate fake data)"""
    user_amount = random.randint(5, 50)
    event_amount = random.randint(3, 10)
    print(f"Amount of users: {user_amount}\nAmount of events: {event_amount}\n")
    # Populating random.randint() amount of users with fake data
    for _ in range(user_amount):
        user = User(
            name=fake.name(), email=fake.email(), phone_number=fake.phone_number()
        )
        db.session.add(user)
    db.session.commit()
    users_query = User.query.all()
    print("Users:")
    for user in users_query:
        print(
            f"id:{user.id}, name:{user.name}, email:{user.email},\
            phone_number:{user.phone_number}, "
            f"events:{user.attended_events}"
        )
    # Populating random.randint() amount of events with fake data
    for _ in range(event_amount):
        event_to_add = Event(
            name=fake.color_name(),
            location=fake.street_name(),
            time="2025-03-15 10:00:00",
            description=fake.catch_phrase(),
            organizer=users_query[random.randint(0, len(users_query) - 1)].id,
            category=random.sample(categories, k=random.randint(1, 3)),
            tags=random.sample(tags, k=random.randint(1, 3)),
        )
        db.session.add(event_to_add)
    db.session.commit()

    events_query = Event.query.all()
    # Populating the events randomly
    print("\nEvents:")
    for event_info in events_query:
        print(
            f"id:{event_info.id}, location:{event_info.location}, time:{event_info.time},"
            f"description:{event_info.description}, organizer:{event_info.organizer}, \
            category:{event_info.category}"
        )
    print("\nPopulating event participants table")
    for ev in events_query:
        selected_users = random.sample(
            users_query, min(random.randint(2, 15), len(users_query))
        )
        print(f"Randomly selected amount of users: {len(selected_users)}")
        for selected_user in selected_users:
            ev.users.append(selected_user)  # Adds selected user to the current event
        db.session.commit()

    # These can be uncommented to see the EventParticipant information line by line
    # event_participations = EventParticipants.query.all()
    # print("\nEvent participation prints:")
    # for p in event_participations:
    # print(f"Event {p.event_id}: User {p.user_id} ")


def populate_single_user(name, email, phone_number=""):
    """Populating single user for tests"""
    if phone_number:
        user = User(name=name, email=email, phone_number=phone_number)
    else:
        user = User(name=name, email=email)
    db.session.add(user)
    db.session.commit()


def populate_single_event(
    name="",
    location="",
    time="",
    organizer=None,
    description="",
    category=None,
    event_tags=None,
):
    """Populates single event"""
    if description and category and event_tags:
        new_event = Event(
            name=name,
            location=location,
            time=time,
            description=description,
            organizer=organizer,
            category=category,
            tags=event_tags,
        )
    else:
        new_event = Event(name=name, location=location, time=time, organizer=organizer)
    db.session.add(new_event)
    db.session.commit()


if __name__ == "__main__":
    create_database()
    with app.app_context():
        db.drop_all()
        db.create_all()
        populate_database()
        users = User.query.all()
        print("\nUser-wise event information:")
        for u in users:
            print(f"User with ID {u.id} is participating in {u.attended_events} events")
        print("\nEvent-wise participant information:")
        events = Event.query.all()
        for e in events:
            participants = [user.name for user in e.users]
            print(
                f"Event {e.id} ({e.name}) participants:"
                f"{', '.join(participants) if participants else 'No participants'}"
            )
        # Print the filtered events
        category_events = Event.query.filter(Event.category.contains("music")).all()
        print("\nFiltered Events:")
        for events in category_events:
            print(f"Name: {events.name},  Categories: {events.category}")

        tags_events = Event.query.filter(Event.tags.contains("jazz-concert")).all()
        print("\nFiltered tags:")
        for event in tags_events:
            print(f"Name: {event.name},  tags: {event.tags}")

        # Print events organized by user
        print()
        for u in users:
            events_organized_by_user = Event.query.filter_by(organizer=u.id).all()
            for e in events_organized_by_user:
                print(f"{e.name} is organized by user {u.name}")
