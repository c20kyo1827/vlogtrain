from flask import Blueprint
from controllers.attractions import blueprint_attractions
from controllers.mrts import blueprint_mrts
from controllers.users import blueprint_users
from controllers.book import blueprint_book
from controllers.order import blueprint_orders

blueprint_routes = Blueprint("blueprint_routes", __name__)

blueprint_routes.register_blueprint(blueprint_attractions, url_prefix="/api")
blueprint_routes.register_blueprint(blueprint_mrts, url_prefix="/api")
blueprint_routes.register_blueprint(blueprint_users, url_prefix="/api")
blueprint_routes.register_blueprint(blueprint_book, url_prefix="/api")
blueprint_routes.register_blueprint(blueprint_orders, url_prefix="/api")