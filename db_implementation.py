import os
import config as cfg
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Engine
from sqlalchemy import event
from datetime import datetime
import mysql.connector


def create_database():
    """Creates the MySQL database with the name cfg.DB_NAME"""
    database = mysql.connector.connect(host=cfg.DB_HOST, user=cfg.DB_USERNAME, passwd=cfg.DB_PASSWORD)
    database_cursor = database.cursor()
    try:
        database_cursor.execute(f"CREATE DATABASE {cfg.DB_NAME}")
    except mysql.connector.errors.DatabaseError as db_error:
        print(f"{db_error.__class__.__name__}:{db_error}")
    finally:
        database_cursor.execute("SHOW DATABASES")
        for databases_found in database_cursor:
            print(databases_found)


# Initialize Flask app
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (f"mysql+pymysql://{cfg.DB_USERNAME}:{cfg.DB_PASSWORD}"
                                         f"@{cfg.DB_HOST}/{cfg.DB_NAME}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# TODO --> tähän pitää luoda table
# events = db.Table(...)


#TODO --> tarkista onko tämä tarpeellinen
@event.listens_for(Engine, "connect")
def set_mysql_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
    cursor.close()


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(128), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(2048))
    participants = db.Column(db.JSON)  # db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    organizer = db.Column(db.String(128))
    category = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    user = db.relationship('User', back_populates='event')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(128), nullable=True)
    event = db.relationship('Event', back_populates='user')


if __name__ == "__main__":
    create_database()
