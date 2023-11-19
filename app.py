from flask import *
from routes.blueprint import blueprint_routes
from flask_cors import CORS
import os

app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
# app.json.ensure_ascii = False
CORS(app)

# Util
@app.route('/util/<path:filename>')
def util_files(filename):
    return send_from_directory(os.path.join(app.root_path, 'util'), filename)

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

app.register_blueprint(blueprint_routes)
app.config.from_object("config")
print(app.config)
app.run(host="0.0.0.0", port=5000)