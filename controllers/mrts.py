from flask import Blueprint, jsonify
from models import mydb_mgr

blueprint_mrts = Blueprint('blueprint_mrts', __name__)
mydb = mydb_mgr.mydb_mgr()
mydb.init()

# TODO
# Use flask_sqlalchemy to modify
@blueprint_mrts.route('/mrts')
def mrts():
    try:
        mrts_list = mydb.get_mrts()
        return jsonify({ "data": [mrt[0] for mrt in mrts_list] })
    except:
        return \
            jsonify({ \
                "error": True, \
                "message": "Server internal error" \
            }), 500