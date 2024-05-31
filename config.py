import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '39048u2joirq@@$i0910'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///../instance/timesheets.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
