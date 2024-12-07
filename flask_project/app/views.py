from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, login_required, logout_user
from . import db
from .models import Account, Event
from . import login_manager  # Import login_manager from the current package (not from flask_login)

main_bp = Blueprint('main', __name__)

# User loader function
@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))

# Login/Signup route
@main_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        action = request.form['action']  # 'login' or 'signup'
        is_organizer = 'is_organizer' in request.form

        if action == 'login':
            user = Account.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('main.home'))
            else:
                flash('Invalid username or password. Please try again.', 'danger')

        elif action == 'signup':
            existing_user = Account.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists. Please choose a different username.', 'danger')
            else:
                new_account = Account(username=username, is_organizer=is_organizer)
                new_account.set_password(password)
                db.session.add(new_account)
                db.session.commit()
                flash('Account created successfully! You can now log in.', 'success')
                return redirect(url_for('main.login'))  # Redirect to login page after signup

    return render_template('login.html')

# Logout route
@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
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

# Settings route
@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
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
                user.set_password(password)
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

    return render_template('profile.html', profile=user)

# Route for event details page
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

# Decline event route
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

@main_bp.route('/home')
@login_required
def home():
    user = current_user  # Get the currently logged-in user
    featured_events = Event.query.limit(6).all()  # Get a limited number of featured events to display on the homepage

    if user.is_organizer:  # Check if the user is an event organizer
        # If the user is an organizer, show the events they manage
        managed_events = Event.query.filter_by(organizer=user.username).all()
        return render_template(
            'home.html', 
            user=user,  # Pass 'user' explicitly to the template
            managed_events=managed_events, 
            featured_events=featured_events
        )
    else:
        # If the user is not an organizer, show the events they are attending
        attended_events = user.event_attendance  # Access the events the user has signed up for
        return render_template(
            'home.html', 
            user=user,  # Pass 'user' explicitly to the template
            attended_events=attended_events, 
            featured_events=featured_events
        )

# Create event route
@main_bp.route('/create_event', methods=['POST'])
@login_required
def create_event():
    if request.method == 'POST':
        event_name = request.form['event_name']
        event_type = request.form['event_type']
        time = request.form['time']
        desc = request.form['desc']
        location = request.form['location']
        date = request.form['date']

        # Associate the event with the current user's ID directly
        new_event = Event(
            event_name=event_name,
            event_type=event_type,
            time=time,
            desc=desc,
            location=location,
            date=date,
            user_id=current_user.id  # Use user_id instead of organizer_id
        )

        db.session.add(new_event)
        db.session.commit()
        flash(f'Event "{event_name}" created successfully!', 'success')
        return redirect(url_for('main.home'))
