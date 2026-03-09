import os
import hashlib
import io
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from commonregex import CommonRegex
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = "vault_master_key_123"

# --- LOGIN CONFIG ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Temporary User Storage (Replace with DB for production)
class User(UserMixin):
    def __init__(self, id): self.id = id

@login_manager.user_loader
def load_user(user_id): return User(user_id)

# --- CONFIGURATION ---
# --- DYNAMIC CLOUD PATHING ---

# This finds the folder where the script is running
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Creates a 'vault_storage' folder inside your project directory
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'vault_storage')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Encryption Setup
# --- FAIL-SAFE KEY LOGIC ---
KEY_FILE = os.path.join(BASE_DIR, "vault.key")

if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "rb") as kf:
        KEY = kf.read()
else:
    # If the key is missing (first time on server), generate it
    KEY = Fernet.generate_key()
    with open(KEY_FILE, "wb") as kf:
        kf.write(KEY)

cipher = Fernet(KEY)

# --- ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Credentials for your demo
        if username == "admin" and password == "cyber2026":
            login_user(User(1))
            return redirect(url_for('index'))
        flash("❌ Invalid credentials. Access Denied.")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f != "vault.key"]
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    file = request.files['file']
    if not file: return redirect(url_for('index'))
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # AI SCAN (The Noisy Logic)
    with open(file_path, 'r', errors='ignore') as f:
        content = f.read()
    
    parsed = CommonRegex(content)
    if parsed.credit_cards or parsed.emails or "password" in content.lower():
        os.remove(file_path)
        flash("🚨 AI BLOCK: Sensitive data (PII) detected in content.")
        return redirect(url_for('index'))

    # ENCRYPTION
    with open(file_path, 'rb') as f: data = f.read()
    with open(file_path, 'wb') as f: f.write(cipher.encrypt(data))

    flash(f"🔒 SUCCESS: '{file.filename}' secured.")
    return redirect(url_for('index'))

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, 'rb') as f: encrypted_data = f.read()
    return send_file(io.BytesIO(cipher.decrypt(encrypted_data)), download_name=filename, as_attachment=True)

if __name__ == '__main__':
    # This only runs when you manually type 'python app.py'
    app.run(host='0.0.0.0', port=5000, debug=True)