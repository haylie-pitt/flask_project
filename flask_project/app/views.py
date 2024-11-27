from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, login_required, logout_user
from . import db
from .models import Account, Event
from . import login_manager  # Import login_manager from the current package (not from flask_login)

main_bp = Blueprint('main', __name__)

# User loader function to get the user by user_id
@login_manager.user_loader
def load_user(user_id):
    # Ensure this method returns a user object (Account instance) for the given user_id
    return Account.query.get(int(user_id))

# Route for the login page (with sign-up functionality built in)
@main_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        action = request.form['action']  # 'login' or 'signup'

        if action == 'login':
            # Check if the account exists
            user = Account.query.filter_by(username=username).first()
            if user and user.check_password(password):  # Check if password is correct
                login_user(user)  # Log the user in
                flash('Login successful!', 'success')
                return redirect(url_for('main.home'))  # Redirect to the homepage
            else:
                flash('Invalid username or password. Please try again.', 'danger')

        elif action == 'signup':
            # Check if the username already exists
            existing_user = Account.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists. Please choose a different username.', 'danger')
            else:
                # Create a new account and hash the password
                new_account = Account(username=username)
                new_account.set_password(password)  # Hash the password before saving
                db.session.add(new_account)
                db.session.commit()
                flash('Account created successfully! You can now log in.', 'success')
                return redirect(url_for('main.login'))  # Redirect to login page after signup

    return render_template('login.html')

# Route for logging out
@main_bp.route('/logout')
@login_required
def logout():
    logout_user()  # Log the user out
    flash('You have been logged out!', 'success')
    return redirect(url_for('main.login'))  # Redirect to login page

# Route for the search functionality
@main_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')  # Get the search term from the query parameter
    if query:
        # Search for events that match the query (case-insensitive)
        events = Event.query.filter(Event.event_name.ilike(f'%{query}%')).all()
        return jsonify([event.event_name for event in events])  # Return the list of event names
    return jsonify([])  # Return empty if no search query

# Route for the settings page
@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required  # This ensures the user must be logged in to access settings
def settings():
    user = current_user  # Get the current logged-in user

    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        desc = request.form['desc']
        hobbies = request.form['hobbies']
        age = request.form['age']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Handle username update
        if username != user.username:
            user.username = username

        # Handle description, hobbies, and age updates
        user.desc = desc
        user.hobbies = hobbies
        user.age = age

        # Handle password update if provided
        if password:
            if password == confirm_password:
                user.set_password(password)  # Hash and update the password
            else:
                flash("Passwords do not match. Please try again.", 'danger')
                return redirect(url_for('main.settings'))  # Stay on settings page if passwords don't match

        # Commit the changes to the database
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.settings'))  # Redirect back to settings page after update

    # If GET request, render the settings page with the current user data
    return render_template('settings.html', user=user)

# Sample homepage route after login
@main_bp.route('/home')
@login_required  # This ensures the user must be logged in to access the homepage
def home():
    return render_template('home.html')