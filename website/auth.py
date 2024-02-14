from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Booking
from .views import get_iso_week_number as wk
from . import db 
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, date

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.

    On GET request, renders the login page.
    On POST request, processes form data to authenticate the user.
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            if user.password == password:
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                if user.role == "student":
                    return redirect(url_for("views.student"))
                elif user.role == "manager":
                    return redirect(url_for('views.manager'))
                elif user.role == "accommodation":
                    return redirect(url_for('views.accommodation'))
                elif user.role == "access":
                    return redirect(url_for('auth.access'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    """
    Logs out the user and redirects to the login page.
    """
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/accommodation/sign-up', methods=['GET', 'POST'])
def sign_up():
    """
    Allows users to sign up.

    On GET request, renders the sign-up page.
    On POST request, processes form data to create a new user profile.
    """
    if request.method == 'POST':
        initials = request.form.get('initials')
        surname = request.form.get('surname')
        email1 = request.form.get('email1')
        email2 = request.form.get('email2')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        role = request.form.get('role')
        
        user = User.query.filter_by(email=email1).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(initials) == 0:
            flash('Enter valid initials', category='error')
        elif len(surname) < 2:
            flash('Enter valid surname', category='error')
        elif email1 != email2:
            flash('Emails do not match', category='error')
        elif len(email1) < 4:
            flash('Enter valid email', category='error')
        elif password1 != password2:
            flash('Passwords do not match', category='error')
        elif len(password1) < 8:
            flash('Password characters must be more than 7', category='error')
        elif len(role) < 1:
            flash('Enter valid role', category='error')
        else:
            new_user = User(initials=initials, surname=surname, email=email1, password=password1, role=role)
            db.session.add(new_user)
            db.session.commit()
            flash('User profile created!', category='success')
            return redirect(url_for('auth.login'))
        
    return render_template("sign_up.html", user=current_user)

@auth.route('/access', methods=['GET', 'POST'])
@login_required
def access():
    """
    Controls access for users.

    On GET request, renders the access page.
    On POST request, checks if the user has access based on booking information.
    """
    if request.method =='POST':
        date_m = date.today()
        week =  wk(date_m.year, date_m.month, date_m.day) 
        user_id = request.form.get("user_id")
        booking_of_interest = Booking.query.filter(Booking.user_booking_id_fk == str(user_id), Booking.week == week+1).all()
        
        if booking_of_interest:
            flash('Booking confirmed, access granted', category='success')
        else:
            flash('Booking not found, contact management for enquiries, Access Denied', category='error')
    return render_template("access.html", user=current_user)
