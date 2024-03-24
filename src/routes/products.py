from flask import Blueprint
from flask import request, jsonify
import bcrypt
from models import db, User, Products
import re
import math
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from utils import APIException
import os
from datetime import datetime

products = Blueprint("products", __name__)

@products.route("/", methods=['GET'])
def load_products():

    args = request.args

    limit = args.get("limit", 10, type=int)
    page = args.get("page", 1, type=int)

    count = Products.query.count()
    total_pages = math.ceil( count / limit )

    products = Products.query.offset( (page - 1) * limit ).limit(limit)

    return {
        "results": [ prod.serialize() for prod in products ],
        "total": count,
        "total_pages": total_pages,
        "page": page
    } , 200

@products.route("/new_product", methods=['POST'])
def create_product():
    body = request.get_json()

    name = body.get("name", None)
    description = body.get("description", '')
    amount = body.get("amount", 1)
    price = body.get("price", None)
    image = body.get("image", None)

    if name == None or price == None:
        return { "message": "request body missing name or price" }, 400
    
    new_product = Products.create(name=name, amount=amount, image=image, description=description, price=price)
    if new_product == None:
        return { "message": "An error occured during product creation" }, 500
    
    return new_product.serialize() , 200

@products.route("/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    product = Products.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    data = request.get_json()
    product.name = data["name"]
    product.description = data["description"]
    product.image = data["image"]
    product.amount = data["amount"]
    product.price = data["price"]
    db.session.commit()
    return jsonify(product.serialize()), 200

@products.route("/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = Products.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"}), 200
