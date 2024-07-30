from flask import Blueprint, request, render_template, redirect, url_for, flash
from models import Feedback
from extensions import db, mail
from flask_mail import Message
import os

# Define the feedback blueprint
feedback = Blueprint('feedback', __name__)

@feedback.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    # Get data from form submission
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    # Create new feedback entry
    new_feedback = Feedback(name=name, email=email, message=message)
    db.session.add(new_feedback)
    db.session.commit()

    # Send thank you email to the person who submitted the feedback
    send_thank_you_email(name, email)

    flash('Kritik dan saran Anda telah dikirim.', 'success')
    return redirect(url_for('feedback.index'))

@feedback.route('/')
def index():
    # Retrieve all feedback from the database, ordered by creation date
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template('feedback/index.html', feedbacks=feedbacks)

def send_thank_you_email(name, email):
    # Create the email message
    msg = Message('Terima Kasih atas Kritik dan Saran Anda',
                  sender=os.getenv('EMAIL_SENDER'),  # Use sender email from .env
                  recipients=[email])  # Send to the email provided in the form
    msg.body = f"Dear {name},\n\nTerima kasih telah memberikan kritik dan saran Anda. Kami sangat menghargainya.\n\nSalam,\nTim To-Do List App"
    
    # Send the email using Flask-Mail
    mail.send(msg)
