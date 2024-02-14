'''
This code is a Flask application with a series of routes and functionalities for managing bookings, menus, and user accounts. Here's a breakdown of the main components:

1. Blueprints and Imports: The code starts with imports from Flask, Flask extensions (like Flask-Login), and the application's models. It also imports datetime for date handling.

2. get_iso_week_number Function: This function calculates the ISO week number for a given date.

3. get_list Function: This function takes a list of booking statuses and organizes them into chunks representing days of the week. It's used to prepare booking information for display.

4. Blueprint Registration: The code registers a Flask Blueprint called views.

5. Routes:
    -/: Renders the home page.
    -/student/: Handles student operations, such as booking meals.
    -/student/view_bookings/: Renders the page to view student's bookings.
    -/student/modify_bookings/: Allows students to modify their bookings.
    -/manager/: Renders the manager's dashboard.
    -/manager/menu/: Handles menu management by the manager.
    -/manager/bookings/: Displays bookings for the current week.
    -/accommodation/: Renders the accommodation page.
    -/accommodation/delete/: Allows deletion of user accounts.
    
6. Route Functions:
    -home(), student(), view_bookings(), modify(), manager(), menu(), bookings(), accommodation(), and delete(): These functions implement the logic for the corresponding routes.

7. Form Processing:
    -The code processes form data submitted by users to book meals or modify bookings.

8. Database Operations:
    -It interacts with the database (presumably a SQLAlchemy database) to add, update, or delete records.

9. Flash Messages: Flash messages are used to provide feedback to users after certain operations.

10. Template Rendering: The routes render HTML templates, passing data as needed for dynamic content generation.
'''

# Import necessary modules and components from Flask and extensions
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Booking, Weekly_menu, Access_Card, Reminder, Booking_Modification_Log
from datetime import datetime, date
import copy
from . import db

# Function to calculate ISO week number for a given date
def get_iso_week_number(year, month, day):
    date_object = datetime(year, month, day)
    week_number = date_object.isocalendar()[1]
    return week_number

# Function to organize booking statuses into chunks representing days of the week
def get_list(booking_list):
    # Define chunk sizes for days of the week
    chunk_sizes = [5, 5, 2, 7]
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Track the index for the current booking
    current_index = 0
    
    # Initialize a list to store booking information
    booking_info = []

    # Loop through each chunk size
    for size in chunk_sizes:
        # Loop through each day in the chunk
        for i in range(size):
            # Determine if the booking for this day is 'Booked' or 'Not Booked'
            if booking_list[current_index] == '1':
                booking_info.append((days[i], 'Booked'))
            else:
                booking_info.append((days[i], 'Not Booked'))
            
            # Increment the index
            current_index += 1

    return booking_info

# Define a Blueprint named 'views' for organizing routes
views = Blueprint('views', __name__)

# Route for the home page
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)

# Route for student operations, such as booking meals
@views.route('/student/', methods=['GET', 'POST'])
@login_required
def student():
    # Processing form data for booking meals
    if request.method == 'POST':
        # Get the ISO week number for the current date
        date_m = date.today()
        week =  get_iso_week_number(date_m.year, date_m.month, date_m.day) 
        
        # Check if a booking for the current week already exists
        current_week_booking_check = Weekly_menu.query.filter(Weekly_menu.week == week).first()
        
        # Process the form data and add it to the database if booking for the week doesn't exist
        if not current_week_booking_check:
            # Retrieve meal choices from the form
            breakfast = request.form.getlist('breakfast')
            lunch = request.form.getlist('lunch')
            brunch = request.form.getlist('brunch')
            supper = request.form.getlist('supper')
            
            # Convert meal choices into a string representation
            meal_type = str(breakfast + lunch + brunch + supper)
            
            # Create a new booking record in the database
            new_booking = Booking(user_booking_id_fk=current_user.user_id, week=week+1, meal_type=meal_type, status='confirmed')
            db.session.add(new_booking)
            db.session.commit()
            
            flash('Your booking was successful', category='success')
        else:
            flash('You have already booked for this week!', category='error')

    return render_template("student.html", user=current_user)

# Route for viewing student's bookings
@views.route('/student/view_bookings/', methods=['GET', 'POST'])
@login_required
def view_bookings():
    # Retrieve the student's bookings from the database
    my_bookings = Booking.query.filter(Booking.user_booking_id_fk == str(current_user.user_id)).all()
    
    # Get the meal types for the last booking and organize them into days of the week
    raw_list = (my_bookings[-1].meal_type).split(', ')
    booking_list = get_list(raw_list)

    return render_template("view_bookings.html", user=current_user, booking_info=booking_list)

# Route for modifying student's bookings
@views.route('/student/modify_bookings/', methods=['GET', 'POST'])
@login_required
def modify():
    if request.method == 'POST':
        # Get the ISO week number for the current date
        date_m = date.today()
        week =  get_iso_week_number(date_m.year, date_m.month, date_m.day)
        
        # Retrieve current booking for the week
        current_booking = Booking.query.filter(Booking.week == week+1).first()
        
        # Delete the current booking
        db.session.delete(current_booking)
        db.session.commit()
        
        # Process the form data for the modified booking
        breakfast = request.form.getlist('breakfast')
        lunch = request.form.getlist('lunch')
        brunch = request.form.getlist('brunch')
        supper = request.form.getlist('supper')
        
        # Convert meal choices into a string representation
        meal_type = str(breakfast + lunch + brunch + supper)
        
        # Create a new booking record in the database
        new_booking = Booking(user_booking_id_fk=current_user.user_id, week=week+1, meal_type=meal_type, status='confirmed')
        db.session.add(new_booking)
        db.session.commit()
        
        flash('Your booking was successfully Updated', category='success')
        return redirect(url_for('views.student'))

    return render_template("modify.html", user=current_user)

# Route for manager's dashboard
@views.route('/manager/', methods=["GET", "POST"])
@login_required
def manager():
    return render_template("manager.html", user=current_user)

# Route for menu management by the manager
@views.route('/manager/menu/', methods=['GET', 'POST'])
@login_required
def menu():
    if request.method == 'POST':
        # Retrieve weekly menu data from the form
        weekly_menu = {
            "breakfast": {
                "monday": request.form.get('breakfast_monday'),
                "tuesday": request.form.get('breakfast_tuesday'),
                "wednesday": request.form.get('breakfast_wednesday'),
                "thursday": request.form.get('breakfast_thursday'),
                "friday": request.form.get('breakfast_friday')
            },
            "brunch": {
                "saturday": request.form.get('brunch_saturday'),
                "sunday": request.form.get('brunch_sunday')
            },
            "supper": {
                "monday": request.form.get('supper_monday'),
                "tuesday": request.form.get('supper_tuesday'),
                "wednesday": request.form.get('supper_wednesday'),
                "thursday": request.form.get('supper_thursday'),
                "friday": request.form.get('supper_friday'),
                "saturday": request.form.get('supper_saturday'),
                "sunday": request.form.get('supper_sunday')
            }
        }
        
        # Get the ISO week number for the current date
        date_m = date.today()
        week =  get_iso_week_number(date_m.year, date_m.month, date_m.day)
        
        # Add the weekly menu to the database
        new_menu = Weekly_menu(week=week+1, menu_content=str(weekly_menu))
        db.session.add(new_menu)
        db.session.commit()
        
        flash('Menu update was successful', category='success')
        return redirect(url_for('views.manager'))
        
    return render_template("menu.html", user=current_user)

# Route for displaying bookings for the current week by the manager
@views.route('/manager/bookings/')
@login_required
def bookings():
    # Get the ISO week number for the current date
    date_m = date.today()
    week =  get_iso_week_number(date_m.year, date_m.month, date_m.day)
    
    # Retrieve student bookings for the current week from the database
    student_bookings = Booking.query.filter(Booking.week == week+1).order_by(Booking.user_booking_id_fk).all()
    
    # Organize booking information for display
    booking_info = {}
    for booking in student_bookings:
        booking_info.setdefault(booking.user_booking_id_fk, []).extend(booking.meal_type.split(', '))

    processed_bookings = {}
    for key, value in booking_info.items():
        processed_bookings[key] = get_list(value)

    return render_template("bookings.html", bookings=processed_bookings, user=current_user)

# Route for managing user accounts - accommodation page
@views.route('/accommodation/')
@login_required
def accommodation():
    return render_template("accommodation.html", user=current_user)

# Route for deleting user accounts
@views.route('/accommodation/delete/', methods=['GET', 'POST'])
@login_required
def delete():
    if request.method =='POST':
        # Get the user ID to be deleted from the form
        user_id = request.form.get("user_id")
        
        # Retrieve the user to be deleted from the database
        user_to_be_deleted = User.query.filter(User.user_id == user_id).first()
        
        # Delete the user from the database
        db.session.delete(user_to_be_deleted)
        db.session.commit()
        
        flash('Deletion successful', category='success')
        
    return render_template("delete.html", user=current_user)
