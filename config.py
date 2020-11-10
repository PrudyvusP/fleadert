import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'indoneSia XeNa'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADED_FILES_DEST = os.path.join(basedir, 'app/static')
    ALLOWED_EXTENSIONS = [".jpg", ".png", ".jpeg", ".gif"]
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1mb
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 8025
    MAIL_USE_TLS = False
    #MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    #MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = 'admin@flask.local'
    FLASKY_MAIL_SUBJECT_PREFIX = 'Flask-local: '
    FLASKY_ADMIN_RECIEVER = 'test_admin@flask.local'