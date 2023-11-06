from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import logging
import jwt
import sys
from models import mydb_mgr

blueprint_users = Blueprint("blueprint_users", __name__)
mydb = mydb_mgr.mydb_mgr()
mydb.init()

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

@blueprint_users.route("/user", methods=["POST"])
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
        member = mydb.get_member(request.json.get("email"))
        if member:
            return \
                jsonify({ \
                    "error": True, \
                    "message": "信箱重複" \
                }), 400
        else:
            mydb.add_member(request.json.get("name"), request.json.get("email"), request.json.get("password"))
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

@blueprint_users.route("/user/auth", methods=["GET"])
def auth_get_sign_in():
    try:
        payload = process_auth_header(request.headers.get("Authorization"))

        if payload == None:
            return jsonify({"data": None})

        return jsonify({"data":{ \
                            "id" : payload["id"], \
                            "name" : payload["name"], \
                            "email" : payload["email"] \
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
    
    
@blueprint_users.route("/user/auth", methods=["PUT"])
def auth_sign_in():
    try:
        member = mydb.get_member(request.json.get("email"), request.json.get("password"))
        if not member:
            return \
                jsonify({ \
                    "error": True, \
                    "message": "帳號或密碼錯誤" \
                }), 400
        else:
            payload = {
                "id" : member[0][0],
                "name" : member[0][2],
                "email" : member[0][1],
                "password" : request.json.get("password"),
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