from flask_login import UserMixin
from app import db
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def check_password(self, password):
        return self.password == password

class Timesheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_hours = db.Column(db.Float, nullable=False)
