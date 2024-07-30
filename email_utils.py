import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email(user_email, tasks):
    sender_email = current_app.config.get('MAIL_USERNAME')
    sender_password = current_app.config.get('MAIL_PASSWORD')
    
    logger.info(f"Sender email: {sender_email}")
    logger.info(f"Sender password: {'*' * len(sender_password) if sender_password else 'Not set'}")

    if not sender_email or not sender_password:
        logger.error("EMAIL_SENDER or EMAIL_PASSWORD not set in configuration.")
        return

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
                    <th style="padding: 8px; text-align: left; background-color: #f2f2f2;">Status</th>
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
                <td style="padding: 8px;">{task.status}</td>
            </tr>
        """

    body += """
            </tbody>
        </table>
        <p>Thank you for using our service. By Muhammad Hamja</p>
    </body>
    </html>
    """

    msg.attach(MIMEText(body, 'html'))

    try:
        logger.info(f"Sending email to {user_email}...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, user_email, text)
        server.quit()
        logger.info(f"Email sent to {user_email}")
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {e}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
