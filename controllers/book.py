import json
from flask import Blueprint, jsonify, request
from datetime import datetime
import logging
import jwt
import sys
from models import mydb_mgr
from controllers.users import process_auth_header

blueprint_book = Blueprint("blueprint_book", __name__)
mydb = mydb_mgr.mydb_mgr()
mydb.init()

logging.root.name = "Book API"
logging.basicConfig(level=logging.INFO,
                format="[%(levelname)-7s] %(name)s - %(message)s",
                stream=sys.stdout)

@blueprint_book.route("/booking", methods=["GET"])
def get_booking():
    try:
        payload = process_auth_header(request.headers.get("Authorization"))

        if payload == None:
            return \
                jsonify({ \
                    "error": True, \
                    "message": "Havn't logged in" \
                }), 403

        bookGroup = mydb.get_booking(payload["id"])
        data = []
        for bookInfo in bookGroup:
            attraction = {
                "id":bookInfo[2],
                "name":bookInfo[6],
                "address":bookInfo[7],
                "image":bookInfo[8]
            }
            data.append(
                {
                    "attraction":attraction,
                    "date":bookInfo[3].isoformat(),
                    "time":' '.join(bookInfo[4]),
                    "price":bookInfo[5]
                }
            )
        
        if data!=[]:
            return \
                jsonify({ \
                    "data": data
                }), 200
        return \
            jsonify({ \
                "data": None
            }), 200

    except Exception as e:
        exc_type, _, exc_tb = sys.exc_info()
        logging.error("Error while getting booking : {error}, type : {type} at line : {line}".format(error=e, type=exc_type, line=exc_tb.tb_lineno))
        return \
            jsonify({ \
                "error": True, \
                "message": "Server internal error" \
            }), 500

@blueprint_book.route("/booking", methods=["POST"])
def new_booking():
    try:
        payload = process_auth_header(request.headers.get("Authorization"))

        if payload == None:
            return \
                jsonify({ \
                    "error": True, \
                    "message": "Havn't logged in" \
                }), 403

        # TODO
        # Support multiple order
        mydb.add_book(payload["id"], request.json.get("attractionId"), request.json.get("date"), request.json.get("time"), request.json.get("price"))
        return \
            jsonify({ \
                "ok": True
            }), 200

    except Exception as e:
        exc_type, _, exc_tb = sys.exc_info()
        logging.error("Error while newing booking : {error}, type : {type} at line : {line}".format(error=e, type=exc_type, line=exc_tb.tb_lineno))
        return \
            jsonify({ \
                "error": True, \
                "message": "Server internal error" \
            }), 500

# TODO
# Should check the book_id's owner should be this member (use member_id)
@blueprint_book.route("/booking", methods=["DELETE"])
def delete_booking():
    try:
        payload = process_auth_header(request.headers.get("Authorization"))

        if payload == None:
            return \
                jsonify({ \
                    "error": True, \
                    "message": "Havn't logged in" \
                }), 403

        # TODO
        # Support multiple order
        mydb.delete_book_all(payload["id"])
        return \
            jsonify({ \
                "ok": True
            }), 200

    except Exception as e:
        exc_type, _, exc_tb = sys.exc_info()
        logging.error("Error while deleting booking : {error}, type : {type} at line : {line}".format(error=e, type=exc_type, line=exc_tb.tb_lineno))
        return \
            jsonify({ \
                "error": True, \
                "message": "Server internal error" \
            }), 500