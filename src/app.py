"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from datetime import timedelta
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db
from flask_jwt_extended import JWTManager
from routes.users import users
from routes.products import products
from routes.drivers import drivers
from routes.customers import customers
from routes.orders import orders

app = Flask(__name__)
app.url_map.strict_slashes = False

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
jwt = JWTManager(app)

app.register_blueprint(users, url_prefix='/users', name='users_bp')
app.register_blueprint(products, url_prefix='/products', name='products_bp')
app.register_blueprint(customers, url_prefix='/customers', name='customers_bp')
app.register_blueprint(drivers, url_prefix='/drivers', name='drivers_bp')
app.register_blueprint(orders, url_prefix='/orders', name='orders_bp')



MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3002))
    app.run(host='0.0.0.0', port=PORT, debug=False)
