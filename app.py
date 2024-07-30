from flask import Flask, redirect, url_for, session, render_template, request
from config import Config
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from apscheduler.schedulers.background import BackgroundScheduler
from extensions import db, mail
from email_utils import send_email
from views import auth, tasks
from models import User, Task
from authlib.integrations.flask_client import OAuth
from authlib.jose import JsonWebKey, jwt
import logging
from dotenv import load_dotenv
import os
import requests
from welcome import welcome

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
mail.init_app(app)

# Configure login manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# Register blueprints
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(tasks, url_prefix='/tasks')
app.register_blueprint(welcome, url_prefix='/')

# Configure OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    client_kwargs={'scope': 'openid profile email', 'prompt': 'select_account'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    redirect_uri=os.getenv('GOOGLE_REDIRECT_URI')
)

# JWKS keys for verifying Google ID tokens
JWKS_URI = 'https://www.googleapis.com/oauth2/v3/certs'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def get_google_public_keys():
    response = requests.get(JWKS_URI)
    return response.json()

def verify_google_id_token(token):
    jwks = get_google_public_keys()
    header = jwt.get_unverified_header(token)
    key = JsonWebKey.import_key(jwks, kid=header['kid'])
    claims = jwt.decode(token, key)
    # Validate claims
    if claims['iss'] != 'https://accounts.google.com':
        raise ValueError('Invalid issuer.')
    claims.validate()
    return claims

@app.route('/login/google')
def google_login():
    redirect_uri = url_for('google_callback', _external=True)
    # Generate nonce and store it in the session
    nonce = os.urandom(16).hex()
    session['nonce'] = nonce
    return google.authorize_redirect(redirect_uri, nonce=nonce)

@app.route('/auth/callback')
def google_callback():
    try:
        token = google.authorize_access_token()
        id_token = token['id_token']
        nonce = session.get('nonce')
        user_info = google.parse_id_token(token, nonce=nonce)

        # Ambil informasi pengguna dari token ID atau endpoint profil
        email = user_info['email']
        username = email  # Gunakan email sebagai username

        user = User.query.filter_by(email=email).first()
        if not user:
            # Karena pengguna Google biasanya tidak memiliki password, Anda bisa memberikan nilai default atau menggunakan hashing untuk menyimpan password kosong.
            # Contoh: hash password default atau kosong (jangan gunakan password kosong dalam produksi)
            password_hash = ''  # Atau hash password default jika diinginkan

            # Tambahkan pengguna baru ke database
            user = User(username=username, email=email, password=password_hash)
            db.session.add(user)
            db.session.commit()

        login_user(user)
        return redirect(url_for('index'))  # Redirect to index.html
    except Exception as e:
        logger.error(f"Error during Google OAuth: {str(e)}")
        return redirect(url_for('auth.login'))



@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return redirect(url_for('auth.login'))

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

def schedule_email():
    with app.app_context():
        logger.info("Running scheduled email job...")
        users = User.query.all()
        for user in users:
            pending_tasks = Task.query.filter_by(user_id=user.id).all()
            if pending_tasks:
                send_email(user.email, pending_tasks)

scheduler = BackgroundScheduler()
scheduler.add_job(func=schedule_email, trigger="interval", minutes=180)
scheduler.start()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
