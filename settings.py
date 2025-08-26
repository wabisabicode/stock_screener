import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite://')
    SECRET_KEY = os.getenv('SECRET_KEY')
