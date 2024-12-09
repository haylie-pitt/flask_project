from flask import Flask
from flask_login import LoginManager
import os

# Initialize Flask app with absolute path for template folder
template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_path)
app.secret_key = 'super_secret_key'

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'main.login'

# Import and register blueprint
from .views import main_bp
app.register_blueprint(main_bp)

# Configure user loader
from .models import Account

@login_manager.user_loader
def load_user(username):
    user_data = Account.find_by_username(username)
    if user_data:
        return Account(**user_data)
    return None
