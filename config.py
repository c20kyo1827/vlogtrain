import os

# TODO
# Check whether move the key setting from app.py to config.py

basedir = os.path.abspath(os.path.dirname(__file__))

JSON_AS_ASCII = False
JSON_ENSURE_ASCII = False
TEMPLATES_AUTO_RELOAD = True
SQLALCHEMY_DATABASE_URI = "mysql://" + os.getenv("MYSQL_USER","root") + ":" + os.getenv("MYSQL_ROOT_PASSWD","root") + "@" + os.getenv("MYSQL_HOST","localhost") + "/VLOG"
SQLALCHEMY_TRACK_MODIFICATIONS = False