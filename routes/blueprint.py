from flask import Blueprint
from controllers.simulate import blueprint_simulate

blueprint_routes = Blueprint("blueprint_routes", __name__)

blueprint_routes.register_blueprint(blueprint_simulate, url_prefix="/api")