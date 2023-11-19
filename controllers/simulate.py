from flask import Blueprint, jsonify, request
import cmd
import os
import subprocess
import urllib.parse

blueprint_simulate = Blueprint('blueprint_simulate', __name__)

@blueprint_simulate.route('/runIverilog', methods=["POST"])
def run_iverilog():
    try:
        data = request.get_json()
        # file_name = urllib.parse.unquote(data["fileName"])
        # decoded_code = urllib.parse.unquote(data["code"])
        file_name = data["fileName"]
        decoded_code = data["code"]
        dir_path = "./tmp"
        cur_path = os.getcwd()

        os.chdir(dir_path)
        with open(file_name, "w") as f:
            f.writelines(decoded_code)
        iverilog_command = "iverilog " + file_name
        process = subprocess.Popen(iverilog_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode==0:
            vvp_command = "vvp a.out"
            runResult = subprocess.run(vvp_command, shell=True, stdout=subprocess.PIPE, text=True)
            result = runResult.stdout
        else:
            result = stderr.decode("utf-8")

        # # Remove the .v .out
        # all_files = os.listdir(os.getcwd())
        # for file_name in all_files:
        #     file_path = os.path.join(os.getcwd(), file_name)
        #     if os.path.isfile(file_path):
        #         _, file_extension = os.path.splitext(file_name)
        #         if file_extension in ['.v', '.out']:
        #             os.remove(file_path)

        os.chdir(cur_path)
        return \
            jsonify({ \
                "ok": True,
                "info": result
            }), 200
    except:
        return \
            jsonify({ \
                "error": True, \
                "message": "Server internal error" \
            }), 500