from app import create_app, db
from app.models import Account, Event, EventAttendance  # Ensure models are imported

app = create_app()

with app.app_context():
    db.create_all()  # This initializes the tables
    print("Database initialized!")
