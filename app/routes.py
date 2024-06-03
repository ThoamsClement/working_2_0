from flask import Blueprint, render_template, request, redirect, url_for, jsonify, Response, flash
from flask_login import login_user, logout_user, current_user, login_required
from .models import db, User, Timesheet
import datetime
import io
import csv

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

@main.route('/')
def index():
    total_hours = db.session.query(db.func.sum(Timesheet.total_hours)).scalar() or 0
    timesheets = Timesheet.query.all()
    return render_template('index.html', timesheets=timesheets, total_hours=total_hours)

@main.route('/add_timesheet', methods=['GET', 'POST'])
def add_timesheet():
    if request.method == 'POST':
        job_name = request.form['job_name']
        description = request.form['description']
        start_time_str = request.form['start_time']
        end_time_str = request.form['end_time']

        start_time = datetime.datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
        end_time = datetime.datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
        total_hours = (end_time - start_time).total_seconds() / 3600

        new_timesheet = Timesheet(
            job_name=job_name,
            description=description,
            start_time=start_time,
            end_time=end_time,
            total_hours=total_hours
        )

        db.session.add(new_timesheet)
        db.session.commit()

        return redirect(url_for('main.index'))

    return render_template('add_timesheets.html')
@main.route('/delete_timesheet/<int:timesheet_id>', methods=['POST'])
def delete_timesheet(timesheet_id):
    timesheet = Timesheet.query.get_or_404(timesheet_id)
    db.session.delete(timesheet)
    db.session.commit()
    flash('Timesheet deleted successfully', 'success')
    return redirect(url_for('main.view_timesheets'))

@main.route('/view_timesheets')
def view_timesheets():
    total_hours = db.session.query(db.func.sum(Timesheet.total_hours)).scalar() or 0
    timesheets = Timesheet.query.all()
    return render_template('view.html', timesheets=timesheets, total_hours=total_hours)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Username already exists!', 'error')

    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))  # 返回登录页面，避免重定向循环

    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
