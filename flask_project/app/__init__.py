from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize db and migration tools globally
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models AFTER initializing the app and db
    with app.app_context():
        from .models import Account, Event, EventAttendance

    # Register blueprints
    from .views import main_bp
    app.register_blueprint(main_bp)

    return app
