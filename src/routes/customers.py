from flask import Blueprint
from flask import request, jsonify
import bcrypt
from models import db, User, Products, Customer, Address
import re
import math
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from utils import APIException, check
import os
from datetime import datetime
from datetime import timedelta

customers = Blueprint("customers", __name__)

@customers.route("/new_customer", methods=['POST'])
def create_customer():
    """Dado la información necesaria, crea un nuevo usuario 
    y almacena la información adicional en la base de datos clasificandolo como 
    un comprador.
    """

    body = request.get_json()

    country = body.get("country", None)
    city = body.get("city", None)
    address = body.get("address", None)

    if city == None:
        return { "message": "City field is missing in request body" }, 400
    if address == None:
        return { "message": "Address field is missing in request body" }, 400
    if country == None:
        return { "message": "Country field is missing in request body" }, 400
    
    email = body.get("email", None)
    name = body.get("name", None)
    lastname = body.get("lastname", None)
    password = body.get("password", None)

    bpassword = bytes(password, 'utf-8')

    salt = bcrypt.gensalt(14)

    hashed_password = bcrypt.hashpw(password=bpassword, salt=salt)

    print( len(hashed_password.decode('utf-8')), len(salt.decode('utf-8')))

    if email != None and password != None:

        if check(email) == False:
            return { "message" : "email format is invalid" }, 400
        
        try:
            new_address = Address(country=country, city=city, address=address)

            db.session.add(new_address)

            new_customer = Customer(email=email, password=hashed_password.decode('utf-8'), address=new_address, salt=salt.decode('utf-8'), name=name, lastname=lastname, createdAt=datetime.utcnow())

            db.session.add(new_customer)

            db.session.commit()

            return { "customer": new_customer.serialize(), "token": create_access_token(identity=email, expires_delta=timedelta(hours=3)) }, 200

        except ValueError as err:

            return { "message": "An unexpected error has occured" }

    else:
        return { "message": "User field missing in request body" }, 400

    return jsonify(body), 200