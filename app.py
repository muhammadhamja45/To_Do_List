from flask import Flask
from config import Config
from models import db, User, Task
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler
from email_utils import send_email
from welcome import welcome
from views import auth, tasks

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(tasks, url_prefix='/tasks')
app.register_blueprint(welcome, url_prefix='/')

def schedule_email():
    with app.app_context():
        users = User.query.all()
        for user in users:
            pending_tasks = Task.query.filter_by(user_id=user.id).all()
            if pending_tasks:
                send_email(user.email, pending_tasks)

scheduler = BackgroundScheduler()
scheduler.add_job(func=schedule_email, trigger="interval", minutes=3)
scheduler.start()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
