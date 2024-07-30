from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Feedback
from extensions import db, mail
from flask_mail import Message

welcome = Blueprint('welcome', __name__)

@welcome.route('/')
def index():
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template('welcome.html', feedbacks=feedbacks)

@welcome.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    new_feedback = Feedback(name=name, email=email, message=message)
    db.session.add(new_feedback)
    db.session.commit()

    # Send thank you email
    send_thank_you_email(name, email)

    flash('Kritik dan saran Anda telah dikirim.', 'success')
    return redirect(url_for('welcome.index'))

def send_thank_you_email(name, email):
    msg = Message('Terima Kasih atas Kritik dan Saran Anda',
                  recipients=[email])
    msg.body = f"Dear {name},\n\nTerima kasih telah memberikan kritik dan saran Anda. Kami sangat menghargainya.\n\nSalam,\nTim To-Do List App.ByMuhammadHamja"
    mail.send(msg)
