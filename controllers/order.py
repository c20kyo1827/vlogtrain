from flask import Blueprint, jsonify, request
from models import mydb_mgr
from datetime import datetime
import logging
import jwt
import requests
import os
import random
import string
import sys
from controllers.users import process_auth_header

blueprint_orders = Blueprint('blueprint_orders', __name__)
mydb = mydb_mgr.mydb_mgr()
mydb.init()

logging.root.name = "Order API"
logging.basicConfig(level=logging.INFO,
                format="[%(levelname)-7s] %(name)s - %(message)s",
                stream=sys.stdout)

@blueprint_orders.route("/orders", methods=["POST"])
def new_order():
    try:
        payload = process_auth_header(request.headers.get("Authorization"))

        if payload == None:
            return \
                jsonify({ \
                    "error": True, \
                    "message": "Havn't logged in" \
                }), 403

        # Contact info not complete
        order = request.json.get("order", None)
        contact = order.get("contact", None)
        if order == None or contact == None:
            return \
                jsonify({ \
                    "error": True, \
                    "message": "Contact Info should not be empty" \
                }), 400

        if contact.get("name", None)==None or contact.get("email", None)==None or contact.get("phone", None)==None:
            return \
                jsonify({ \
                    "error": True, \
                    "message": "Contact Info should not be empty" \
                }), 400
        
        # Request
        url = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": os.getenv("PARTNER_KEY", "test")
        }
        data = {
            "prime": request.json.get("prime", None),
            "partner_key": os.getenv("PARTNER_KEY", "test"),
            "merchant_id": "c20kyo1827_CTBC",
            "details": "TapPay Test",
            "amount": order.get("price", None),
            "cardholder": {
                "phone_number": "+8869" + contact.get("phone", None)[2:],
                "name": contact.get("name", None),
                "email": contact.get("email", None),
            }
        }

        result = requests.post(url, headers=headers, json=data, timeout=30).json()
        characters = string.ascii_letters + string.digits
        random_characters = ''.join(random.choice(characters) for _ in range(5))
        order_number = datetime.now().strftime("%Y%m%d%H%M%S") + str(payload["id"]) + "_" + random_characters
        if result["status"] != 0:
            return \
                jsonify({
                    "data": {
                        "number": order_number,
                        "payment": {
                            "status": result["status"],
                            "message": "付款失敗"
                        }
                    }
                }), 200
        # TODO
        # Support multiple order
        mydb.delete_book_all(payload["id"])
        trip = request.json.get("order").get("trip")
        mydb.add_order(
            order_number,
            payload["id"],
            trip.get("attraction").get("id"),
            contact.get("name"), contact.get("email"), contact.get("phone"),
            trip.get("date"), trip.get("time"), order.get("price"),
            result["status"]
        )
        return \
            jsonify({
                "data": {
                    "number": order_number,
                    "payment": {
                        "status": result["status"],
                        "message": "付款成功"
                    }
                }
            }), 200

        

    except Exception as e:
        exc_type, _, exc_tb = sys.exc_info()
        logging.error("Error while create ordering : {error}, type : {type} at line : {line}".format(error=e, type=exc_type, line=exc_tb.tb_lineno))
        return \
            jsonify({ \
                "error": True, \
                "message": "Server internal error" \
            }), 500

@blueprint_orders.route("/order/<string:orderNumber>", methods=["GET"])
def get_order_from_id(orderNumber):
    try:
        payload = process_auth_header(request.headers.get("Authorization"))

        if payload == None:
            return \
                jsonify({ \
                    "error": True, \
                    "message": "Havn't logged in" \
                }), 403

        order = mydb.get_order(payload["id"], orderNumber)
        if order == []:
            return \
                jsonify({ \
                    "data": None
                }), 200
        attraction = mydb.get_attraction(order[0][3])
        images = mydb.get_images_by_id(order[0][3])

        # TODO
        return \
            jsonify({ \
                "data": {
                    "number": order[0][1],
                    "price": order[0][10],
                    "trip": {
                        "attraction": {
                            "id": order[0][3],
                            "name": attraction[0][1],
                            "address": attraction[0][3],
                            "image": images[0][0]
                        },
                        "date": order[0][8].isoformat(),
                        "time": ' '.join(order[0][9])
                    },
                    "contact": {
                        "name": order[0][5],
                        "email": order[0][6],
                        "phone": order[0][7]
                    },
                    "status": order[0][4]
                }
            }), 200

    except Exception as e:
        exc_type, _, exc_tb = sys.exc_info()
        logging.error("Error while create ordering : {error}, type : {type} at line : {line}".format(error=e, type=exc_type, line=exc_tb.tb_lineno))
        return \
            jsonify({ \
                "error": True, \
                "message": "Server internal error" \
            }), 500