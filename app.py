from flask import *
from flask_cors import CORS
import cmd
import subprocess
import urllib.parse
app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
# app.json.ensure_ascii = False
CORS(app)

# Pages
@app.route("/")
def index():
	return render_template("index.html")

@app.route("/api/sendVerilog", endpoint="/api/sendVerilog", methods=['POST'])
def send_verilog():
	data = request.get_json()
	decoded_code = urllib.parse.unquote(data["code"])
	with open("test.v", "w") as f:
		f.writelines(decoded_code)
	print(decoded_code)
	iverilog_command = "iverilog test.v"
	process = subprocess.Popen(iverilog_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = process.communicate()
	
	if process.returncode==0:
		vvp_command = "vvp a.out"
		runResult = subprocess.run(vvp_command, shell=True, stdout=subprocess.PIPE, text=True)
		print("This is result")
		print(runResult.stdout)
		print(type(runResult.stdout))
		result = runResult.stdout
	else:
		result = stderr.decode("utf-8")
	return \
		jsonify({ \
			"ok": True,
			"info": result
		}), 200

app.config.from_object("config")
print(app.config)
app.run(host="0.0.0.0", port=5000)