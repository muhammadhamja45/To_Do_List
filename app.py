from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_name = db.Column(db.String(255), nullable=False)
    task_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
@login_required
def add_task():
    task_name = request.form.get('task_name')
    task_date = request.form.get('task_date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    new_task = Task(user_id=current_user.id, task_name=task_name, task_date=task_date, start_time=start_time, end_time=end_time)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if task and task.user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('index'))

def send_email(user_email, tasks):
    sender_email = "muhammadhamja45@gmail.com"
    sender_password = "bnwf kcjl nsvc rixu"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = "Pending Tasks Notification"

    body = """
    <html>
    <body>
        <h2>Here is the list of your pending tasks:</h2>
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <thead>
                <tr>
                    <th style="padding: 8px; text-align: left; background-color: #f2f2f2;">Task</th>
                    <th style="padding: 8px; text-align: left; background-color: #f2f2f2;">Date</th>
                    <th style="padding: 8px; text-align: left; background-color: #f2f2f2;">Start Time</th>
                    <th style="padding: 8px; text-align: left; background-color: #f2f2f2;">End Time</th>
                </tr>
            </thead>
            <tbody>
    """

    for task in tasks:
        body += f"""
            <tr>
                <td style="padding: 8px;">{task.task_name}</td>
                <td style="padding: 8px;">{task.task_date}</td>
                <td style="padding: 8px;">{task.start_time}</td>
                <td style="padding: 8px;">{task.end_time}</td>
            </tr>
        """

    body += """
            </tbody>
        </table>
        <p>Thank you for using our service.</p>
    </body>
    </html>
    """

    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, user_email, text)
        server.quit()
        print(f"Email sent to {user_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def schedule_email():
    with app.app_context():
        users = User.query.all()
        for user in users:
            pending_tasks = Task.query.filter_by(user_id=user.id).all()
            if pending_tasks:
                send_email(user.email, pending_tasks)

scheduler = BackgroundScheduler()
scheduler.add_job(func=schedule_email, trigger="interval", minutes=2)
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)
