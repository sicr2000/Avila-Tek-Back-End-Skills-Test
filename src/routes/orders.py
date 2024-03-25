from flask import Blueprint
from flask import request, jsonify
import bcrypt
from models import db, User, Products, Customer, Address, Order, Driver
import re
import math
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from utils import APIException, check
import os
from datetime import datetime
from datetime import timedelta

orders = Blueprint("orders", __name__)


@orders.route("/", methods=['GET'])
@jwt_required()
def get_all_orders():

    try:
        all_orders = Order.query.all()

        return [ orden.serialize() for orden in all_orders ]

    except ValueError as err:
        return {"message": "failed to retrive orders " + err}, 500


@orders.route("/new_order", methods=['POST'])
@jwt_required()
def new_order():

    body = request.get_json()

    delivery_email = body.get("delivery", None)
    customer_email = body.get("customer", None)

    if delivery_email != None:
        delivery = Driver.query.filter_by(email=delivery_email).one_or_none()
        
    if customer_email != None:
        customer = Customer.query.filter_by(email=customer_email).one_or_none()

        items = body.get("products", [])
        
        products = []

        for i in items:
            products.append( Products.query.get(i) )    

        new_order = Order(customer=customer, delivery=delivery)

        new_order.products = products

        try:
            db.session.add(new_order)
            db.session.commit()

            return new_order.serialize(), 200
        
        except ValueError as err:
            return { "message" : "Something go wrong :(" }, 500


    else:
        return { "Something is missing or incorrect" }, 500
    
