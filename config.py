import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '39048u2joirq@@$i0910'
    SQLALCHEMY_DATABASE_URI = 'mariadb+pymysql://Sign_howmebill:743b42785d81cc89d60c6d817f051cbbb85f942b@wys.h.filess.io:3305/Sign_howmebill'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    INSTANCE_PATH = '/tmp'


