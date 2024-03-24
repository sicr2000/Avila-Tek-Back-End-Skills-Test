from flask import Blueprint
from flask import request, jsonify
import bcrypt
from models import db, User, Products, Driver
import re
import math
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from utils import APIException, check
import os
from datetime import datetime

drivers = Blueprint("drivers", __name__)

@drivers.route("/new_driver", methods=['POST'])
def create_driver():
    """Dado la información necesaria crea un nuevo usuario 
    y almacena la información adicional en la base de datos 
    clasificandolo como un conductor.
    """

    body = request.get_json()

    email = body.get("email", None)
    name = body.get("name", None)
    lastname = body.get("lastname", None)
    password = body.get("password", None)
    serial_plate = body.get("serial_plate", None)

    bpassword = bytes(password, 'utf-8')
    salt = bcrypt.gensalt(14)
    hashed_password = bcrypt.hashpw(password=bpassword, salt=salt)

    if email != None and password != None:

      if check(email) == False:
        return { "message": "email format is invalid" }, 400 

      try:
        
        new_driver = Driver(name=name, lastname=lastname, email=email, password=hashed_password.decode('utf-8'), serial_plate=serial_plate, salt=salt.decode('utf-8'), createdAt=datetime.utcnow())

        db.session.add(new_driver)

        db.session.commit()

        return new_driver.serialize(), 200

      except ValueError as err:

        return { "message": "An unexpected error has occured" }

    else:
        return { "message": "User field missing in request body" }, 400

    return jsonify(body), 200