from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from datetime import datetime
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'xp_secret_key'  # for session handling

DATA_FILE = 'users.json'

def load_users():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def update_class(level):
    if level < 10:
        return "Rookie"
    elif level < 20:
        return "Beginner"
    elif level < 30:
        return "Fighter"
    elif level < 40:
        return "Elite"
    elif level < 50:
        return "Boss"
    else:
        return "Ascended"

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
    else:
        return render_template('login.html', error="Invalid username or password")

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))

    username = session['username']
    users = load_users()
    user = users[username]

    # Total stat
    total_stat = sum(user['stats'].values())

    # XP bar
    level = user['level']
    current_xp = user['xp']
    xp_needed = level * 100
    xp_percent = int((current_xp / xp_needed) * 100) if xp_needed else 0

    today = datetime.now().strftime("%Y-%m-%d")
    if today not in user['xp_history']:
        user['xp_history'][today] = 0

    save_users(users)
    return render_template('status.html',
                           user=user,
                           username=username,
                           total_stat=total_stat,
                           xp_percent=xp_percent,
                           today=today)

@app.route('/update', methods=['POST'])
def update():
    if 'username' not in session:
        return 'Unauthorized', 403

    data = request.json
    users = load_users()
    user = users[session['username']]

    # Update stats
    if 'stats' in data:
        user['stats'] = data['stats']

    # Add XP and check level-up
    if 'add_xp' in data:
        add_xp = data['add_xp']
        user['xp'] += add_xp
        today = datetime.now().strftime("%Y-%m-%d")
        user['xp_history'][today] = user['xp_history'].get(today, 0) + add_xp

        while user['xp'] >= user['level'] * 100:
            user['xp'] -= user['level'] * 100
            user['level'] += 1
            user['class'] = update_class(user['level'])

    # Update tasks
    if 'tasks' in data:
        user['tasks'] = data['tasks']

    # Update rank
    if 'rank' in data:
        user['rank'] = data['rank']

    save_users(users)
    return jsonify(success=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
