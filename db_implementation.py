from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import os

# Initialize Flask app
app = Flask(__name__)

# MySQL Configuration
DB_USERNAME = "your_mysql_user"
DB_PASSWORD = "your_mysql_password"
DB_HOST = "localhost"  # Change if your MySQL is hosted elsewhere
DB_NAME = "events_db"

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(128), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(2048))
    participants = db.Column(db.JSON) #db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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



    