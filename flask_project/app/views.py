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
        is_organizer = 'is_organizer' in request.form  # Check if the 'is_organizer' checkbox was checked

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
                new_account = Account(username=username, is_organizer=is_organizer)
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
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        desc = request.form['desc']
        hobbies = request.form['hobbies']
        age = request.form['age']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Handle first_name and last_name update
        if first_name != user.first_name:
            user.first_name = first_name
        if last_name != user.last_name:
            user.last_name = last_name

        # Handle description, hobbies, and age updates
        user.desc = desc
        user.hobbies = hobbies
        user.age = age

        # Handle username update
        if username != user.username:
            user.username = username

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

# Route for the profile page
@main_bp.route('/profile')
@login_required
def profile():
    user = current_user  # Get the current logged-in user

    if not user:
        flash("You need to be logged in to view your profile.", 'danger')
        return redirect(url_for('main.login'))  # Redirect to login page if no user is found

    # Debugging print statements (optional, remove in production)
    print(user)  # Add a print statement to check the current_user object

    return render_template('profile.html', profile=user)

# Route for event details page (updated to events_details.html)
@main_bp.route('/event/<int:event_id>')
@login_required
def event_details(event_id):
    event = Event.query.get_or_404(event_id)  # Get event by ID or return 404 if not found
    return render_template('events_details.html', event=event)

# Route for signing up for an event (RSVP)
@main_bp.route('/signup/<int:event_id>')
@login_required
def signup(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user not in event.user_id_attendance:
        event.user_id_attendance.append(current_user)
        db.session.commit()
        flash(f"You have successfully signed up for {event.event_name}!", 'success')
    else:
        flash("You are already signed up for this event.", 'info')
    return redirect(url_for('main.event_details', event_id=event.id))

# Route for declining an event (RSVP decline)
@main_bp.route('/decline/<int:event_id>')
@login_required
def decline(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user in event.user_id_attendance:
        event.user_id_attendance.remove(current_user)
        db.session.commit()
        flash(f"You have successfully declined {event.event_name}.", 'success')
    else:
        flash("You haven't signed up for this event.", 'info')
    return redirect(url_for('main.event_details', event_id=event.id))

# Sample homepage route after login
@main_bp.route('/home')
@login_required  # This ensures the user must be logged in to access the homepage
def home():
    featured_events = Event.query.limit(6).all()  # Show events
    return render_template('home.html', featured_events=featured_events)
