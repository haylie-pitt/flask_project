from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_user, login_required, logout_user
from . import db
from .models import Account, Event
from datetime import datetime

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
                flash('Invalid username or password.', 'danger')

        elif action == 'signup':
            existing_user = Account.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists.', 'danger')
            else:
                new_account = Account(username=username, is_organizer=is_organizer)
                new_account.set_password(password)
                db.session.add(new_account)
                db.session.commit()
                flash('Account created successfully!', 'success')
                return redirect(url_for('main.login'))

    return render_template('login.html')

# Logout route
@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!', 'success')
    return redirect(url_for('main.login'))

# Home route
@main_bp.route('/home')
@login_required
def home():
    if current_user.is_organizer:
        managed_events = Event.query.filter_by(organizer_id=current_user.id).all()
        return render_template('home.html', managed_events=managed_events)
    else:
        featured_events = Event.query.limit(6).all()
        return render_template('home.html', featured_events=featured_events)

# Events route
@main_bp.route('/events')
@login_required
def events():
    search_query = request.args.get('search', '')

    if current_user.is_organizer:
        events = Event.query.filter_by(organizer_id=current_user.id)
    else:
        events = Event.query.filter(Event.date >= datetime.utcnow())

    if search_query:
        events = events.filter(Event.event_name.ilike(f"%{search_query}%"))

    return render_template('events.html', events=events.all(), search_query=search_query)

# Event details route
@main_bp.route('/event/<int:event_id>')
@login_required
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user.is_organizer:
        attendee_list = event.user_id_attendance
        return render_template('events_details.html', event=event, attendee_list=attendee_list)
    return render_template('events_details.html', event=event)

# Edit event route
@main_bp.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    if not current_user.is_organizer:
        flash("You don't have permission to edit this event.", 'danger')
        return redirect(url_for('main.home'))

    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        event.event_name = request.form['event_name']
        event.date = request.form['date']
        event.time = request.form['time']
        event.location = request.form['location']
        event.description = request.form['description']
        db.session.commit()
        flash(f"{event.event_name} has been updated successfully.", 'success')
        return redirect(url_for('main.event_details', event_id=event.id))

    return render_template('edit_event.html', event=event)

# Cancel event route
@main_bp.route('/event/<int:event_id>/cancel')
@login_required
def cancel_event(event_id):
    if not current_user.is_organizer:
        flash("You don't have permission to cancel this event.", 'danger')
        return redirect(url_for('main.home'))

    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash(f"{event.event_name} has been canceled.", 'success')
    return redirect(url_for('main.events'))

# Profile route
@main_bp.route('/profile')
@login_required
def profile():
    user = current_user

    if user.is_organizer:
        managed_events = Event.query.filter_by(organizer_id=user.id).all()
        return render_template('profile.html', profile=user, managed_events=managed_events)
    else:
        attended_events = user.attending_events
        return render_template('profile.html', profile=user, attended_events=attended_events)

# Settings route
@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user = current_user

    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.desc = request.form['desc']
        user.hobbies = request.form['hobbies']
        user.age = request.form['age']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if username != user.username:
            user.username = username

        if password:
            if password == confirm_password:
                user.set_password(password)
            else:
                flash("Passwords do not match.", 'danger')
                return redirect(url_for('main.settings'))

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.settings'))

    return render_template('settings.html', user=user)

# Signup route
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

# Search route
@main_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if query:
        events = Event.query.filter(Event.event_name.ilike(f'%{query}%')).all()
        return jsonify([event.event_name for event in events])
    return jsonify([])
