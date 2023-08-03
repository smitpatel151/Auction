import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = 'Kinjal patel'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = 'Enter your email id here'
    MAIL_PASSWORD = 'Enter your password'
    ADMINS = ['Enter the admin email ids in a list format']
    TRACK_USAGE_USE_FREEGEOTP = False
    TRACK_USAGE_INCLUDE_OR_EXCLUDE_VIEWS = 'include'
    smit = ""
