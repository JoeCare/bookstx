import os
from os import getenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base config."""
    SECRET_KEY = getenv('SECRET_KEY')
    SESSION_COOKIE_NAME = getenv('SESSION_COOKIE_NAME')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URI')
    SQLALCHEMY_ECHO = True


class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR,
                                                          'app/app.db')
    # DATABASE_URI = "sqlite:///:memory:"
