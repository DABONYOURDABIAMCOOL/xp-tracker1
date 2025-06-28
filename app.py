from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import json, os, datetime
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'XP_TRACKER_SECRET'
DATA_FILE = 'data/users.json'

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def get_class(level):
    if level < 10:
        return "Rookie"
    elif level < 20:
        return "Novice"
    elif level < 30:
        return "Apprentice"
    elif level < 40:
        return "Elite"
    elif level < 50:
        return "Master"
    return "Legend"

@app.route('/', methods=['GET'])
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    users = load_users()
    if username in users and users[username]['password'] == password:
        session['username'] = username
        return redirect(url_for('dashboard'))
    return "Invalid login"

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))
    users = load_users()
    username = session['username']
    user_data = users[username]
    today = datetime.date.today().isoformat()

    # Create leaderboard
    leaderboard = sorted([
        {
            "username": uname,
            "level": u['level'],
            "xp": u['xp'],
            "class": get_class(u['level']),
            "total": sum(u['stats'].values())
        } for uname, u in users.items()
    ], key=lambda x: x['level'], reverse=True)

    return render_template('status.html',
        username=username,
        user_data=user_data,
        stats=user_data['stats'],
        level=user_data['level'],
        xp=user_data['xp'],
        xp_today=user_data['xp_log'].get(today, 0),
        xp_needed=100 * user_data['level'],
        class_name=get_class(user_data['level']),
        leaderboard=leaderboard
    )

@app.route('/update_xp', methods=['POST'])
def update_xp():
    if 'username' not in session:
        return '', 403
    username = session['username']
    users = load_users()
    xp_gain = int(request.form['xp'])
    user = users[username]
    user['xp'] += xp_gain

    # Log daily XP
    today = datetime.date.today().isoformat()
    user['xp_log'][today] = user['xp_log'].get(today, 0) + xp_gain

    while user['xp'] >= 100 * user['level']:
        user['xp'] -= 100 * user['level']
        user['level'] += 1

    save_users(users)
    return jsonify({
        "xp": user['xp'],
        "level": user['level'],
        "xp_needed": 100 * user['level'],
        "class": get_class(user['level'])
    })

@app.route('/add_stat', methods=['POST'])
def add_stat():
    if 'username' not in session:
        return '', 403
    stat = request.form['stat']
    username = session['username']
    users = load_users()
    users[username]['stats'][stat] += 1
    save_users(users)
    return '', 200

@app.route('/add_task', methods=['POST'])
def add_task():
    return '', 200  # Handled in JS

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
