from flask import Flask, render_template, request, redirect, session, jsonify
import json, os, datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key'
DATA_FILE = 'data/users.json'

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def get_title(level):
    if level < 10:
        return "Rookie"
    elif level < 20:
        return "Beginner"
    elif level < 30:
        return "Fighter"
    elif level < 40:
        return "Elite"
    elif level < 50:
        return "Specialist"
    else:
        return "Legend"

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        uname = request.form['username']
        pwd = request.form['password']
        if uname in users and users[uname]['password'] == pwd:
            session['username'] = uname
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    users = load_users()
    uname = session['username']
    user_data = users[uname]
    level = user_data.get('level', 0)
    xp = user_data.get('xp', 0)
    class_title = get_title(level)
    date_today = datetime.datetime.now().strftime('%d %b %Y')
    leaderboard = sorted([
        {
            'name': u,
            'level': users[u].get('level', 0)
        } for u in users
    ], key=lambda x: x['level'], reverse=True)
    return render_template(
        'status.html',
        username=uname,
        user_data=user_data,
        xp=xp,
        level=level,
        class_title=class_title,
        date_today=date_today,
        leaderboard=leaderboard
    )

@app.route('/update', methods=['POST'])
def update():
    users = load_users()
    uname = session['username']
    data = request.json
    users[uname].update(data)
    save_users(users)
    return jsonify(success=True)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')
