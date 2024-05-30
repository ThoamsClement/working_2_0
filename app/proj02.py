from flask import Flask, render_template, request, redirect, url_for, Response, jsonify, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import csv
import datetime
import io
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import quote as url_quote
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = '39048u2joirq@@$i0910'  

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timetable.db'
db = SQLAlchemy(app)
Migrate(app,db)
# User class for Flask-Login
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Get database connection and cursor
def get_db_connection():
    conn = sqlite3.connect('timesheets.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create table
def create_table():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS timesheets
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  job_name TEXT,
                  description TEXT,
                  start_time TIMESTAMP,
                  end_time TIMESTAMP,
                  total_hours REAL)''')
    conn.commit()
    conn.close()

# Close database connection
def close_db_connection(exception=None):
    conn = get_db_connection()
    conn.close()

# Create table on startup
create_table()

@app.route('/')
def index():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT SUM(total_hours) FROM timesheets")
    total_hours = c.fetchone()[0] or 0
    
    c.execute("SELECT * FROM timesheets")
    timesheets = c.fetchall()
    conn.close()
    return render_template('index.html', timesheets=timesheets, total_hours=total_hours)

@app.route('/add_timesheet', methods=['GET', 'POST'])
def add_timesheet():
    if request.method == 'POST':
        job_name = request.form['job_name']
        description = request.form['description']
        start_time_str = request.form['start_time']
        end_time_str = request.form['end_time']
        
        # Perform validation and data processing
        start_time = datetime.datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
        end_time = datetime.datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')

        total_hours = calculate_total_hours(start_time, end_time)

        # Insert timesheet data into database
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO timesheets (job_name, description, start_time, end_time, total_hours) VALUES (?, ?, ?, ?, ?)",
                  
                  (job_name, description, start_time, end_time, total_hours))
        conn.commit()
        conn.close()
        
        # Redirect to view timesheets page
        return redirect(url_for('view_timesheets'))
    
    return render_template('add_timesheets.html')
def calculate_total_hours(start_time, end_time):
    time_diff = end_time - start_time
    total_hours = time_diff.total_seconds() / 3600
    return total_hours
# 在 app.py 中添加如下代码

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            hashed_password = generate_password_hash(password)  # 使用哈希函数加密密码
            new_user = User(username=username, password=password)  # 存储加密后的密码
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists!', 'error')
    return render_template('register.html')
@app.route('/download_timesheets_csv')
def download_timesheets_csv():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM timesheets")
    timesheets = c.fetchall()
    
    output = io.StringIO()
    fieldnames = ['job_name', 'description', 'start_time', 'end_time']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for timesheet in timesheets:
        writer.writerow({
            'job_name': timesheet['job_name'],
            'description': timesheet['description'],
            'start_time': timesheet['start_time'],
            'end_time': timesheet['end_time']
        })
    output.seek(0)
    conn.close()
    return Response(output, mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=timesheets.csv'})

@app.route('/api/total_hours')
def get_total_hours():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT SUM(total_hours) FROM timesheets")
    total_hours = c.fetchone()[0] or 0
    
    c.execute("SELECT * FROM timesheets")
    timesheets = [{'job_name': row['job_name'], 'description': row['description'], 'start_time': row['start_time'], 'end_time': row['end_time'], 'total_hours': row['total_hours']} for row in c.fetchall()]
    conn.close()
    return jsonify({'total_hours': total_hours, 'timesheets': timesheets})

@app.route('/view_timesheets')
def view_timesheets():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT SUM(total_hours) FROM timesheets")
    total_hours = c.fetchone()[0] or 0
    c.execute("SELECT * FROM timesheets")
    timesheets = c.fetchall()
    conn.close()
    return render_template('view.html', timesheets=timesheets, total_hours=total_hours)

@app.route('/api/timesheets')
def get_timesheets():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM timesheets")
    timesheets = c.fetchall()
    conn.close()
    return jsonify({'timesheets': [dict(timesheet) for timesheet in timesheets]})

@app.route('/delete_timesheet/<int:timesheet_id>', methods=['POST'])
@login_required
def delete_timesheet(timesheet_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM timesheets WHERE id=?", (timesheet_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
    
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False)
