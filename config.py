import os

# TODO
# Check whether move the key setting from app.py to config.py

basedir = os.path.abspath(os.path.dirname(__file__))

JSON_AS_ASCII = False
JSON_ENSURE_ASCII = False
TEMPLATES_AUTO_RELOAD = True
SQLALCHEMY_DATABASE_URI = "mysql://username:password@localhost/db_name"
SQLALCHEMY_TRACK_MODIFICATIONS = False