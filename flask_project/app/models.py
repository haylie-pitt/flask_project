from . import db

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(255))
    hobbies = db.Column(db.String(255))
    age = db.Column(db.String(20))
    event_attendance = db.relationship('Event', secondary='event_attendance')

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    organizer = db.Column(db.String(100))
    time = db.Column(db.String(50))
    desc = db.Column(db.String(255))
    location = db.Column(db.String(255))
    date = db.Column(db.String(20))
    user_id_attendance = db.relationship('Account', secondary='event_attendance')

class EventAttendance(db.Model):
    __tablename__ = 'event_attendance'
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)