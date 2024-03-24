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

customers = Blueprint("customers", __name__)

def check(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    # pass the regular expression
    # and the string into the fullmatch() method
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False

@customers.route("/new_customer", methods=['POST'])
def create_customer():

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

            db.