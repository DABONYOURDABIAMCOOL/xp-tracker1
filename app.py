from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

DATA_FILE = 'data/users.json'

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def get_class_title(level):
    if level < 10:
        return "Rookie"
    elif level < 20:
        return "Beginner"
    elif level < 30:
        return "Fighter"
    elif level < 40:
        return "Elite"
    elif level < 50:
        return "Ace"
    elif level < 60:
        return "Warrior"
    elif level < 70:
        return "Champion"
    elif level < 80:
        return "Master"
    elif level < 90:
        return "Grandmaster"
    else:
        return "Legend"

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    users = load_users()

    if username in users and users[username]['password'] == password:
        session['username'] = username
        return redirect(url_for('dashboard'))
    return 'Invalid credentials', 401

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))

    users = load_users()
    username = session['username']
    user = users[username]
    user_data = user  # 🔥 FIX: This allows status.html to access user_data['class']

    # Auto-update level title
    user_data['class'] = get_class_title(user['level'])

    save_users(users)  # Save updates if class was missing before

    return render_template('status.html',
        username=username,
        stats=user['stats'],
        xp=user['xp'],
        level=user['level'],
        user_data=user_data,
        leaderboard=sorted([
            {
                'username': uname,
                'level': u['level']
            }
            for uname, u in users.items()
        ], key=lambda x: x['level'], reverse=True)
    )

@app.route('/update', methods=['POST'])
def update():
    if 'username' not in session:
        return 'Unauthorized', 403

    users = load_users()
    username = session['username']
    user = users[username]

    data = request.get_json()
    user['stats'] = data.get('stats', user['stats'])
    user['xp'] = data.get('xp', user['xp'])
    user['level'] = data.get('level', user['level'])

    save_users(users)
    return 'Success', 200

if __name__ == '__main__':
    app.run(debug=True)
