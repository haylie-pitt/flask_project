import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Define file paths for JSON storage
data_dir = os.path.join(os.path.dirname(__file__), 'data')
users_file = os.path.join(data_dir, 'users.json')
events_file = os.path.join(data_dir, 'events.json')

# Ensure the data directory exists
os.makedirs(data_dir, exist_ok=True)

# Initialize empty JSON files if needed
for file in [users_file, events_file]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({}, f, indent=4)


# JSON Storage Class
class JSONStorage:
    @staticmethod
    def load_data(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    @staticmethod
    def save_data(file_path, data):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)


# User Account Class
class Account(JSONStorage):
    def __init__(self, username, password, first_name="", last_name="", desc="", hobbies="", age="", is_organizer=False, event_attendance=None):
        self.username = username
        self.password = generate_password_hash(password) if not password.startswith("scrypt:") else password
        self.first_name = first_name
        self.last_name = last_name
        self.desc = desc
        self.hobbies = hobbies
        self.age = age
        self.is_organizer = is_organizer
        self.event_attendance = event_attendance or []

    def save(self):
        users = self.load_data(users_file)
        users[self.username] = self.__dict__
        self.save_data(users_file, users)

    @staticmethod
    def find_by_username(username):
        users = JSONStorage.load_data(users_file)
        return users.get(username)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # Flask-Login properties
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username


# Event Class
class Event(JSONStorage):
    def __init__(self, event_name, event_type, organizer, time, desc, location, date, tags=None):
        self.event_name = event_name
        self.event_type = event_type
        self.organizer = organizer
        self.time = time
        self.desc = desc
        self.location = location
        self.date = date
        self.tags = tags or []
        self.user_id_attendance = []

    def save(self):
        events = self.load_data(events_file)
        event_id = str(len(events) + 1)
        events[event_id] = self.__dict__
        self.save_data(events_file, events)

    @staticmethod
    def find_by_id(event_id):
        events = JSONStorage.load_data(events_file)
        return events.get(event_id)
