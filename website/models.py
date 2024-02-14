"""
This module defines SQLAlchemy models for a Flask application related to user management, bookings, menus, access cards, reminders, and booking modification logs.

Classes:
- User: Represents a user in the system.
- Booking: Represents a booking made by a user for a specific week and meal type.
- Weekly_menu: Represents a weekly menu with its content.
- Access_Card: Represents an access card associated with a user.
- Reminder: Represents a reminder associated with a user.
- Booking_Modification_Log: Represents a log entry for modifications made to bookings by users.

Attributes:
- user_id: Unique identifier for a user.
- initials: Initials of the user.
- surname: Surname of the user.
- username: Username of the user.
- password: Password of the user.
- email: Email address of the user.
- role: Role of the user in the system.
- booking_id: Unique identifier for a booking.
- user_booking_id_fk: Foreign key referencing the user who made the booking.
- week: Week number for the booking.
- meal_type: Type of meal booked.
- status: Status of the booking.
- menu_id: Unique identifier for a weekly menu.
- menu_content: Content of the weekly menu.
- card_id: Unique identifier for an access card.
- user_card_id_fk: Foreign key referencing the user associated with the access card.
- rfid_code: RFID code associated with the access card.
- reminder_id: Unique identifier for a reminder.
- user__reminder_fk: Foreign key referencing the user associated with the reminder.
- reminder_type: Type of reminder.
- date: Date and time of the reminder.
- log_entry_id: Unique identifier for a log entry in the booking modification log.
- log_booking_fk: Foreign key referencing the booking associated with the log entry.
- log_user_id_fk: Foreign key referencing the user associated with the log entry.
- modification_date: Date and time of the modification.
- modification_text: Text describing the modification.
"""

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    """User model representing users of the application."""
    
    user_id = db.Column(db.Integer, primary_key=True)
    initials = db.Column(db.String(5))
    surname = db.Column(db.String(50))
    username = db.Column(db.String(100))
    password = db.Column(db.String(255))
    email = db.Column(db.String(255))
    role = db.Column(db.String(20))
    
    def __repr__(self):
        """Representation of the User object."""
        return f'{self.user_id},{self.initials}, {self.surname}, {self.email},  {self.role}'
    
    def get_id(self):
        """Method required by Flask-Login for retrieving user ID."""
        return str(self.user_id)

class Booking(db.Model, UserMixin):
    """Model representing bookings made by users."""
    
    booking_id = db.Column(db.Integer, primary_key=True)
    user_booking_id_fk = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    week = db.Column(db.Integer, db.ForeignKey('weekly_menu.week'))
    meal_type = db.Column(db.String(20))
    status = db.Column(db.String(20))
    user_booking_relationship = db.relationship('User')
    
    def __repr__(self):
        """Representation of the Booking object."""
        return f'[{self.user_booking_id_fk}, {self.meal_type}]'

class Weekly_menu(db.Model, UserMixin):
    """Model representing weekly menus."""
    
    menu_id = db.Column(db.Integer, primary_key=True)
    week = db.Column(db.Integer)
    menu_content = db.Column(db.String(1000))
    Weekly_menu_booking_relationship = db.relationship('Booking')

class Access_Card(db.Model, UserMixin):
    """Model representing access cards."""
    
    card_id = db.Column(db.Integer, primary_key=True)
    user_card_id_fk = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    rfid_code = db.Column(db.String(20))
    card_user_relationship = db.relationship('User')

class Reminder(db.Model, UserMixin):
    """Model representing reminders for users."""
    
    reminder_id = db.Column(db.Integer, primary_key=True)
    user__reminder_fk = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    reminder_type = db.Column(db.String(20))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    reminder_user_relationship = db.relationship("User")

class Booking_Modification_Log(db.Model, UserMixin):
    """Model representing logs for booking modifications."""
    
    log_entry_id = db.Column(db.Integer, primary_key=True)
    log_booking_fk = db.Column(db.Integer, db.ForeignKey('booking.booking_id'))
    log_user_id_fk = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    modification_date = db.Column(db.DateTime(timezone=True), default=func.now())
    modification_text = db.Column(db.String(10000))
    modification_user_relationship = db.relationship("User")
    modification_booking_relationship = db.relationship("Booking")
