from flask import Flask
from config import Config
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler
from extensions import db, mail
from email_utils import send_email
from views import auth, tasks
from models import User, Task  # Pastikan model User dan Task diimpor
import welcome  # Ini harus diimpor setelah inisialisasi db dan mail
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(tasks, url_prefix='/tasks')
    app.register_blueprint(welcome.welcome, url_prefix='/')

    def schedule_email():
        with app.app_context():
            logger.info("Running scheduled email job...")
            users = User.query.all()
            logger.info(f"Found {len(users)} users.")
            for user in users:
                pending_tasks = Task.query.filter_by(user_id=user.id).all()
                logger.info(f"User {user.email} has {len(pending_tasks)} pending tasks.")
                if pending_tasks:
                    logger.info(f"Attempting to send email to {user.email} with {len(pending_tasks)} pending tasks.")
                    send_email(user.email, pending_tasks)

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=schedule_email, trigger="interval", minutes=1)
    scheduler.start()

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
