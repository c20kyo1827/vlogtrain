from flask import Blueprint, jsonify, request
from models import mydb_mgr

blueprint_attractions = Blueprint('blueprint_attractions', __name__)
mydb = mydb_mgr.mydb_mgr()
mydb.init()

# TODO
# Optimize the data process
# It looks like that there are so many redundant steps
# Consider the flask_sqlalchemy

@blueprint_attractions.route('/attractions')
def attractions():
    try:
        if request.args.get("page").isdigit():
            attrct = mydb.get_attractions_by_page_keyword(request.args.get("page"), request.args.get("keyword"))
            attrct_next = mydb.get_attractions_by_page_keyword(int(request.args.get("page"))+1, request.args.get("keyword"))
            if attrct_next==[]:
                next_page = None
            else:
                next_page = int(request.args.get("page"))+1
            data = []
            for info in attrct:
                category = mydb.get_category_by_id(info[0])
                mrt = mydb.get_mrt_by_id(info[0])
                images = [image[1] for image in mydb.get_images_by_id(info[0])]
                mrt = None if mrt==[] else mrt[0][1]
                data.append( \
                    { \
                        "id": info[0], \
                        "name": info[1], \
                        "category": category[0][1], \
                        "description": info[2], \
                        "address": info[3], \
                        "transport": info[4], \
                        "mrt": mrt, \
                        "lat": info[5], \
                        "lng": info[6], \
                        "images": images \
                    } \
                )

            return jsonify({ \
                        "nextPage": next_page, \
                        "data": data
                    })
        else:
            return \
                jsonify({ \
                    "error": True, \
                    "message": "Argument page is wrong" \
                }), 500
    except:
        return \
            jsonify({ \
                "error": True, \
                "message": "Server internal error" \
            }), 500

@blueprint_attractions.route('/attraction/<int:attractionId>')
def attraction(attractionId):
    try:
        if isinstance(attractionId,int):
            attrct = mydb.get_attraction(attractionId)
            category = mydb.get_category_by_id(attractionId)
            mrt = mydb.get_mrt_by_id(attractionId)
            images = [image[1] for image in mydb.get_images_by_id(attractionId)]
            mrt = None if mrt==[] else mrt[0][1]
            return jsonify({ \
                        "data": { \
                            "id": attrct[0][0], \
                            "name": attrct[0][1], \
                            "category": category[0][1], \
                            "description": attrct[0][2], \
                            "address": attrct[0][3], \
                            "transport": attrct[0][4], \
                            "mrt": mrt, \
                            "lat": attrct[0][5], \
                            "lng": attrct[0][6], \
                            "images": images \
                        } \
                    })
        else:
            return \
                jsonify({ \
                    "error": True, \
                    "message": "attraction id is not integer" \
                }), 400
    except:
        return \
            jsonify({ \
                "error": True, \
                "message": "Server internal error" \
            }), 500