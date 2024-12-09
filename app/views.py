from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash
from flask_login import current_user, login_user, login_required, logout_user
from .models import Account, JSONStorage
from . import login_manager  
import os

# Define events file path
events_file = os.path.join(os.path.dirname(__file__), 'data', 'events.json')

main_bp = Blueprint('main', __name__)

# User loader function
@login_manager.user_loader
def load_user(username):
    user_data = Account.find_by_username(username)
    if user_data:
        return Account(**user_data)
    return None

# Login/Signup route
@main_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        action = request.form['action']  
        is_organizer = 'is_organizer' in request.form

        if action == 'login':
            user_data = Account.find_by_username(username)
            if user_data and check_password_hash(user_data['password'], password):
                user = Account(**user_data)
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('main.home'))
            else:
                flash('Invalid username or password. Please try again.', 'danger')

        elif action == 'signup':
            if Account.find_by_username(username):
                flash('Username already exists. Please choose a different username.', 'danger')
            else:
                new_account = Account(username, password, is_organizer=is_organizer)
                new_account.save()
                flash('Account created successfully! You can now log in.', 'success')
                return redirect(url_for('main.login'))  

    return render_template('login.html')

# Logout route
@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!', 'success')
    return redirect(url_for('main.login'))  

# Search functionality
@main_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')  
    events = JSONStorage.load_data(events_file)

    if query:
        results = [event for event in events.values() if query.lower() in event['event_name'].lower()]
        return render_template('events.html', events=results)

    flash('No events found.', 'warning')
    return redirect(url_for('main.home'))

# Update User Settings Route
@main_bp.route('/update_settings', methods=['POST'])
@login_required
def update_settings():
    user_data = Account.find_by_username(current_user.username)
    if user_data:
        # Update user profile data
        user_data['first_name'] = request.form['first_name']
        user_data['last_name'] = request.form['last_name']
        user_data['desc'] = request.form['desc']
        user_data['hobbies'] = request.form['hobbies']
        user_data['age'] = request.form['age']
        
        # Save changes
        Account(**user_data).save()
        flash('Profile updated successfully!', 'success')
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('main.settings'))

# Event Details Route
@main_bp.route('/event/<event_id>')
def event_details(event_id):
    events = JSONStorage.load_data(events_file)
    event = events.get(event_id)
    if event:
        return render_template('event_details.html', event=event, event_key=event_id)
    flash('Event not found.', 'danger')
    return redirect(url_for('main.home'))
