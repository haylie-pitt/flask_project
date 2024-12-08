from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db

class Account(db.Model, UserMixin):  # Add UserMixin here
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    desc = db.Column(db.String(255))
    hobbies = db.Column(db.String(255))
    age = db.Column(db.String(20))
    is_organizer = db.Column(db.Boolean, default=False)  # Add this line to track organizer status
    event_attendance = db.relationship('Event', secondary='event_attendance')

    # Set the password after hashing
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Check if the password matches the hashed password
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    organizer = db.Column(db.String(100))
    time = db.Column(db.String(50))
    desc = db.Column(db.String(255))
    location = db.Column(db.String(255))
    date = db.Column(db.String(20))
    tags = db.Column(db.String(255), nullable=True)  # New field for tags
    user_id_attendance = db.relationship('Account', secondary='event_attendance')
    
class EventAttendance(db.Model):
    __tablename__ = 'event_attendance'
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)