from app import create_app, db  # Ensure 'create_app' and 'db' are correctly imported
from app.models import Event, Account  # Import your models

def initialize_database():
    """
    Initialize the database and create tables.
    """
    app = create_app()  # Create the Flask app instance
    with app.app_context():  # Ensure the app context is active
        # Drop all tables (optional for development)
        db.drop_all()

        # Create all tables
        db.create_all()

        # Add optional sample data
        add_sample_data()

        print("Database has been initialized successfully!")

def add_sample_data():
    """
    Add sample data to the database for testing.
    """
    # Create a sample user (organizer)
    sample_user = Account(
        username="test_organizer",
        first_name="John",
        last_name="Doe",
        is_organizer=True
    )
    sample_user.set_password("test_password")
    db.session.add(sample_user)

    # Create sample events associated with the organizer
    sample_event1 = Event(
        event_name="Flask Workshop",
        description="Learn the basics of Flask web development.",
        date="2024-12-15",
        time="10:00",
        location="Online",
        tags="Flask,Python,Workshop",
        organizer=sample_user.username  # Associate with the sample user
    )
    sample_event2 = Event(
        event_name="Hackathon 2024",
        description="An exciting hackathon for coders of all levels.",
        date="2024-12-20",
        time="09:00",
        location="Pittsburgh",
        tags="Hackathon,Coding,Event",
        organizer=sample_user.username  # Associate with the sample user
    )

    db.session.add(sample_event1)
    db.session.add(sample_event2)

    # Commit changes to the database
    db.session.commit()
    print("Sample data added successfully!")


if __name__ == "__main__":
    initialize_database()
