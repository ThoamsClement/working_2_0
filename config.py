import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '39048u2joirq@@$i0910'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql://avnadmin:AVNS_zjUUX4W9PeQYT-KZHm-@mysql-cc9afa6-hippoasie-91bc.f.aivencloud.com:20147/defaultdb?ssl-mode=REQUIRED')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    INSTANCE_PATH = '/tmp'


