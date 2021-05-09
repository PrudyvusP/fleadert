import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'indoneSia XeNa'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = False  # changes in templates without reloading a page
    UPLOADED_FILES_DEST = os.path.join(basedir, 'app', 'static', 'avatars')
    ALLOWED_EXTENSIONS = [".jpg", ".png", ".jpeg", ".gif"]
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 1mb
    TASKS_PER_PAGE = 7
    KEY_WORD_FOR_BOSS = os.environ.get('KEY_WORD_FOR_BOSS')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    MAIL_SUBJECT_PREFIX = 'FleaderT - '


class ProdConfig(object):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'indoneSia XeNa'
    SQLALCHEMY_DATABASE_URI = \
        f"mysql+pymysql://{os.environ.get('MYSQL_USER')}:{os.environ.get('MYSQL_PASSWORD')}@localhost/fleadert"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADED_FILES_DEST = os.path.join(basedir, 'app', 'static', 'avatars')
    ALLOWED_EXTENSIONS = [".jpg", ".png", ".jpeg", ".gif"]
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 1mb
    TASKS_PER_PAGE = 7
    KEY_WORD_FOR_BOSS = os.environ.get('KEY_WORD_FOR_BOSS')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    MAIL_SUBJECT_PREFIX = 'FleaderT - '