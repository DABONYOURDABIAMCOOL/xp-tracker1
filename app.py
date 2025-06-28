from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATA_FILE = 'data/users.json'

# ----------- Utilities -----------
def load_users():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def calculate_total(stats):
    return sum(stats.values())

def calculate_level(xp):
    level = 0
    required_xp = 100
    while xp >= required_xp:
        xp -= required_xp
        level += 1
        required_xp += 100
    return level, xp, required_xp

def get_class_title(level):
    titles = [
        "Rookie", "Novice", "Adept", "Pro", "Elite",
        "Master", "Legend", "Mythic", "Ascended", "Godlike"
    ]
    return titles[min(level // 10, len(titles)-1)]

# ----------- Routes -----------
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    users = load_users()

    if username in users and users[username]['password'] == password:
        session['username'] = username
        return redirect(url_for('dashboard'))
    return "Invalid credentials", 401

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))

    users = load_users()
    user = users[session['username']]
    stats = user['stats']
    xp = user['xp']
    level, current_xp, next_level_xp = calculate_level(xp)
    class_title = get_class_title(level)

    today = datetime.now().strftime("%Y-%m-%d")

    return render_template('status.html',
                           username=session['username'],
                           stats=stats,
                           xp=current_xp,
                           level=level,
                           next_level_xp=next_level_xp,
                           class_title=class_title,
                           today=today,
                           leaderboard=sorted([
                               {
                                   "username": uname,
                                   "level": calculate_level(u["xp"])[0]
                               }
                               for uname, u in users.items()
                           ], key=lambda x: x['level'], reverse=True))

@app.route('/update_stat', methods=['POST'])
def update_stat():
    if 'username' not in session:
        return 'Unauthorized', 401

    data = request.json
    stat = data['stat']
    direction = data['direction']

    users = load_users()
    user = users[session['username']]
    if direction == 'up':
        user['stats'][stat] += 1
    elif direction == 'down' and user['stats'][stat] > 0:
        user['stats'][stat] -= 1

    user['stats']['Total'] = calculate_total({k: v for k, v in user['stats'].items() if k != "Total"})
    save_users(users)
    return 'OK', 200

@app.route('/add_xp', methods=['POST'])
def add_xp():
    if 'username' not in session:
        return 'Unauthorized', 401

    data = request.json
    xp_to_add = int(data['xp'])

    users = load_users()
    user = users[session['username']]
    user['xp'] += xp_to_add
    save_users(users)

    return jsonify({"xp": user['xp']}), 200

@app.route('/timer_update', methods=['POST'])
def timer_update():
    if 'username' not in session:
        return 'Unauthorized', 401

    data = request.json
    stat = data['stat']
    hours = int(data['hours'])

    users = load_users()
    user = users[session['username']]
    user['stats'][stat] += hours
    user['stats']['Total'] = calculate_total({k: v for k, v in user['stats'].items() if k != "Total"})

    save_users(users)
    return 'OK', 200

@app.route('/reset_tasks', methods=['POST'])
def reset_tasks():
    if 'username' not in session:
        return 'Unauthorized', 401

    users = load_users()
    user = users[session['username']]
    user['tasks'] = []  # Clears all tasks
    save_users(users)
    return 'OK', 200

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'username' not in session:
        return 'Unauthorized', 401

    data = request.json
    task = data['task']
    xp = int(data['xp'])

    users = load_users()
    user = users[session['username']]
    if 'tasks' not in user:
        user['tasks'] = []

    user['tasks'].append({'name': task, 'xp': xp})
    save_users(users)
    return 'OK', 200

@app.route('/complete_task', methods=['POST'])
def complete_task():
    if 'username' not in session:
        return 'Unauthorized', 401

    data = request.json
    index = data['index']

    users = load_users()
    user = users[session['username']]
    xp = user['tasks'][index]['xp']
    user['xp'] += xp
    del user['tasks'][index]

    save_users(users)
    return 'OK', 200

@app.route('/get_user_data')
def get_user_data():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    users = load_users()
    user = users[session['username']]

    return jsonify(user)

# ----------- Main Run -----------
if __name__ == '__main__':
    app.run(debug=True)
