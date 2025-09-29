import os


class Config(object):
    FLASK_APP = os.getenv('FLASK_APP', 'stock_screener')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', '1')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite://')
    SECRET_KEY = os.getenv('SECRET_KEY')
