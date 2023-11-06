import os
import json
import sys
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PARENT_DIR)
from models import mydb_mgr

# TODO
# Check the comman, colon, and space in the string.
# Check whether it needs to be removed?
attractions = []
def parse(file_path):
    with open(file_path, encoding="utf-8") as f:
        data_json = json.load(f)
        for list in data_json["result"]["results"]:
            attraction_dict = {}
            attraction_dict["id"] = list["_id"]
            attraction_dict["name"] = list["name"]
            attraction_dict["category"] = list["CAT"]
            attraction_dict["description"] = list["description"]
            attraction_dict["address"] = list["address"]
            attraction_dict["transport"] = list["direction"]
            attraction_dict["mrt"] = list["MRT"]
            attraction_dict["lng"] = list["longitude"]
            attraction_dict["lat"] = list["latitude"]
            attractions.append(attraction_dict)

            tokens = list["file"].lower().split("https")
            img_list = []
            for token in tokens:
                if token.endswith(".mp3") or token.endswith(".flv") or token=="":
                    continue
                img_list.append("https"+token)
            attraction_dict["images"] = img_list

if __name__=="__main__":
    file_path = os.path.join(PARENT_DIR, "data", "taipei-attractions.json")
    parse(file_path)
    mydb = mydb_mgr.mydb_mgr()
    mydb.reset()
    mydb.add_attraction_mrt(attractions)
    # mydb.show()