from flask import Blueprint
from controllers.simulate import blueprint_simulate
from controllers.member import blueprint_members

blueprint_routes = Blueprint("blueprint_routes", __name__)

blueprint_routes.register_blueprint(blueprint_simulate, url_prefix="/api")
blueprint_routes.register_blueprint(blueprint_members, url_prefix="/api")