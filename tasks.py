 
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from models import Task, db

def send_email(subject, body, to_email):
    from_email = "your_email@example.com"
    from_password = "your_password"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

def notify_tasks():
    tasks = Task.query.all()
    for task in tasks:
        body = f"Task: {task.activity}\nDescription: {task.description}\nDate: {task.date}\nDecline Date: {task.decline_date}"
        send_email("Task Notification", body, "recipient@example.com")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=notify_tasks, trigger="interval", minutes=15)
    scheduler.start()
    return scheduler
