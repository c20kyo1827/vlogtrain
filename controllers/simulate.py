import logging
import re
import sys
from flask import Blueprint, jsonify, request
from util.vcd2json import vcd2json
import cmd
import os
import subprocess
import urllib.parse

blueprint_simulate = Blueprint('blueprint_simulate', __name__)

logging.root.name = "Iverilog API"
logging.basicConfig(level=logging.INFO,
                format="[%(levelname)-7s] %(name)s - %(message)s",
                stream=sys.stdout)

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

        # Generate the waveform
        print(result)
        match = re.search(r'\b\w+\.vcd\b', result)
        waveform_file = ""
        if match:
            vcd_file_name =  match.group()
            print(vcd_file_name)
            python_script_path = os.path.join('..', 'util', 'vcd2json', 'vcd2json.py')
            script_arguments  = "--file"
            print(python_script_path)
            check = subprocess.run(['python', python_script_path, script_arguments, vcd_file_name], check=True, text=True)
            print(check.stdout)
            waveform_file = os.path.join("..", "tmp", vcd_file_name.split(".")[0]+".svg")
            print(waveform_file)

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
                "info": result,
                "waveform": waveform_file
            }), 200
    except Exception as e:
        exc_type, _, exc_tb = sys.exc_info()
        logging.error("Error : {error}, type : {type} at line : {line}".format(error=e, type=exc_type, line=exc_tb.tb_lineno))
        return \
            jsonify({ \
                "error": True, \
                "message": "Server internal error" \
            }), 500