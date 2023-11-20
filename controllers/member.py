from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import logging
import jwt
import sys
from models import mysql_mgr

blueprint_members = Blueprint("blueprint_members", __name__)
sql_manager = mysql_mgr.mysql_mgr("VLOG")
sql_manager.init()

logging.root.name = "User API"
logging.basicConfig(level=logging.INFO,
                format="[%(levelname)-7s] %(name)s - %(message)s",
                stream=sys.stdout)

secret_key = "f1#39gA9psa"

def process_auth_header(auth_header):
    if auth_header is None:
        return None

    split_header = auth_header.split()
    if len(split_header) != 2 or split_header[0].lower() != "bearer" or split_header[1].lower() == "null":
        return None

    payload = jwt.decode(split_header[1], secret_key, algorithms="HS256")
    if payload["exp"] is None or datetime.utcnow() > datetime.utcfromtimestamp(payload["exp"]):
        return None
    
    return payload

@blueprint_members.route("/user", methods=["POST"])
def sign_up():
    try:
        if request.is_json==False:
            raise Exception("Request is not json")
        # TODO
        # Check the password
        # def is_valid_password(password):
        #     has_upper = any(char.isupper() for char in password)
        #     has_symbol = any(char in string.punctuation for char in password)
        #     is_match_size = len(password)>=8 and len(password)<=20
        #     return [has_upper, has_symbol, is_match_size]
        data = {
            "email" : request.json.get("email")
        }
        print(data)
        member = sql_manager.get_member(data)
        if member:
            return \
                jsonify({ \
                    "error": True, \
                    "message": "Repeated email" \
                }), 400
        else:
            data = {
                "name" : request.json.get("name"),
                "email" : request.json.get("email"),
                "password" : request.json.get("password"),
            }
            sql_manager.add_member(data)
            return \
                jsonify({ \
                    "ok": True \
                }), 200
    except Exception as e:
        exc_type, _, exc_tb = sys.exc_info()
        logging.error("Error while signing up : {error}, type : {type} at line : {line}".format(error=e, type=exc_type, line=exc_tb.tb_lineno))
        return \
            jsonify({ \
                "error": True, \
                "message": "Server internal error" \
            }), 500

@blueprint_members.route("/user/auth", methods=["GET"])
def auth_get_sign_in():
    try:
        payload = process_auth_header(request.headers.get("Authorization"))

        if payload == None:
            return jsonify({"data": None})

        return jsonify({"data":{ \
                            "id" : payload["id"], \
                            "name" : payload["name"], \
                            "email" : payload["email"], \
                            "solved_problem" : payload["solved_problem"] \
                        } \
                    })
    except Exception as e:
        exc_type, _, exc_tb = sys.exc_info()
        logging.error("Error while get authorizing : {error}, type : {type} at line : {line}".format(error=e, type=exc_type, line=exc_tb.tb_lineno))
        return \
            jsonify({ \
                "error": True, \
                "message": "Server internal error" \
            }), 500
    
    
@blueprint_members.route("/user/auth", methods=["PUT"])
def auth_sign_in():
    try:
        data = {
            "email" : request.json.get("email"),
            "password" : request.json.get("password")
        }
        member = sql_manager.get_member(data)
        print(member)
        if not member:
            return \
                jsonify({ \
                    "error": True, \
                    "message": "Email or password are error" \
                }), 400
        else:
            payload = {
                "id" : member.id,
                "name" : member.name,
                "email" : member.email,
                "password" : request.json.get("password"),
                "solved_problem": member.total_solve_problems,
                "exp": datetime.utcnow() + timedelta(days=7)
            }
            try:
                token = jwt.encode(payload, secret_key, algorithm="HS256")
            except Exception as e:
                logging.error("Error while creating token : {}".format(e))
                return \
                    jsonify({ \
                        "error": True, \
                        "message": "Error while creating token" \
                    }), 400
            
            return \
                jsonify({ \
                    "token": token\
                }), 200
    except Exception as e:
        exc_type, _, exc_tb = sys.exc_info()
        logging.error("Error while signing in : {error}, type : {type} at line : {line}".format(error=e, type=exc_type, line=exc_tb.tb_lineno))
        return \
            jsonify({ \
                "error": True, \
                "message": "Server internal error" \
            }), 500