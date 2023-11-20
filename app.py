from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from routes.blueprint import blueprint_routes
from models.models import db, migrate
import os

app=Flask(__name__)
CORS(app)

# Util
@app.route('/util/<path:filename>')
def util_files(filename):
    return send_from_directory(os.path.join(app.root_path, 'util'), filename)
# TODO
# Use the S3 to store
@app.route('/tmp/<path:filename>')
def tmp_files(filename):
    return send_from_directory(os.path.join(app.root_path, 'tmp'), filename)

# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/playground")
def playground():
	return render_template("playground.html")
@app.route("/problem_sets")
def problem_sets():
	return render_template("problem_sets.html")
@app.route("/problem/<id>")
def problem(id):
	return render_template("problem.html")
@app.route("/member")
def member():
	return render_template("member.html")

app.register_blueprint(blueprint_routes)
app.config.from_object("config")
db.init_app(app)
migrate.init_app(app, db)
print(app.config)
with app.app_context():
    db.create_all()
app.run(host="0.0.0.0", port=5000)