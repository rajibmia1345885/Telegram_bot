from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Files to sync with the bot
VERIFICATIONS_FILE = 'verifications.json'
IP_MAP_FILE = 'ip_tracking.json'
BANNED_FILE = 'banned_users.json'

def load_json(file):
    if os.path.exists(file):
        with open(file, 'r') as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def home():
    return "<h1>IP Verification Server is Running!</h1>"

@app.route('/verify')
def verify():
    user_id = request.args.get('user_id')
    if not user_id:
        return "<h1>Error: User ID missing!</h1>", 400
    
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in user_ip:
        user_ip = user_ip.split(',')[0].strip()

    # Load data
    verifications = load_json(VERIFICATIONS_FILE)
    ip_map = load_json(IP_MAP_FILE)
    banned_users = load_json(BANNED_FILE)
    if not isinstance(banned_users, list): banned_users = []

    user_id_str = str(user_id)
    
    # Check if IP already linked to another user
    if user_ip in ip_map:
        linked_users = ip_map[user_ip]
        if user_id_str not in linked_users:
            # Multi-account detected!
            if user_id_str not in banned_users:
                banned_users.append(user_id_str)
                save_json(BANNED_FILE, banned_users)
            
            return f"<h1>🚫 Access Denied!</h1><p>Multi-account detected from IP: {user_ip}. Your account has been banned.</p>", 403
    else:
        ip_map[user_ip] = [user_id_str]
        save_json(IP_MAP_FILE, ip_map)

    # Save verification
    verifications[user_id_str] = {
        "ip": user_ip,
        "time": datetime.now().isoformat()
    }
    save_json(VERIFICATIONS_FILE, verifications)

    return f"<h1>✅ Verification Successful!</h1><p>User ID: {user_id}<br>IP Address: {user_ip}</p><p>You can now go back to the bot and use the /like command.</p>"

if __name__ == '__main__':
    # Run on port 5000
    app.run(host='0.0.0.0', port=5000)
