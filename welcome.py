from flask import Blueprint, render_template

welcome = Blueprint('welcome', __name__)

@welcome.route('/')
def index():
    return render_template('welcome.html')
