from flask import Blueprint
from flask import request, jsonify
import bcrypt
from models import db, User
import re
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from utils import APIException, check
import os
from datetime import datetime


users = Blueprint("users", __name__)


@users.route("/user", methods=["GET"])
@jwt_required()
def get_user():
    """Dado la información necesaria entrega la 
    información de un usuario. 
    
    Esta ruta requiere autenticación para 
    retornar la información.
    """
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify(user.serialize()), 200
    return jsonify({"message": "User not found"}), 404


@users.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    """Dado la información necesaria entrega un listado de 
    todos los usuarios. 
    
    Esta ruta requiere autenticación para 
    retornar la información.
    """
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify("User has changed their email"), 404
    user = user.serialize()
    users = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users))
    return jsonify(all_users), 200

@users.route("/user", methods=["POST"])
def create_user():
    """Dado la información necesaria crea un nuevo
    usuario y lo agrega a la base de datos. 
    """
    body = request.get_json()
    if (
        "email" in body.keys()
        and body["email"] != ""
        and body["email"] != None
        and "password" in body.keys()
        and body["password"] != ""
        and body["password"] is not None
        and "name" in body.keys()
        and body["name"] != ""
        and body["name"] is not None
        and "lastname" in body.keys()
        and body["lastname"] != ""
        and body["lastname"] is not None
    ):
        name = body.get("name").capitalize()
        lastname = body.get("lastname").capitalize()
        email = body.get("email").lower()
        password = body.get("password")
        possible_user = User.query.filter_by(email=email).first()
        if possible_user:
            return jsonify({"message": "User " + email + " already exists"}), 422
        if check_email(email) == False:
            return jsonify({"message": "Email format is invalid"}), 400
        if len(password) < 6:
            return jsonify({"message": "Password must be at least 6 characters"}), 400
        bpassword = bytes(password, "utf-8")
        salt = bcrypt.gensalt(14)
        hashed_password = bcrypt.hashpw(password=bpassword, salt=salt)
        user = User(
            name=name,
            lastname=lastname,
            email=email,
            createdAt=datetime.now(),
            password=hashed_password.decode("utf-8"),
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "A user has been created", "email": user.email}), 201
    return (
        jsonify(
            {
                "message": "Attributes name, lastname, email and password are ne"
            }
        ),
        400,
    )

@users.route("/user/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    """Dado la información necesaria actualiza la
    información del usuario.
    
    Esta ruta requiere autenticación para 
    retornar la información.
    """
    body = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": f"User {email} already exists"}), 422
    
    keys = ["name", "lastname", "email", "password"]
    for key in keys:
        if key in body and body[key] and body[key] != "":
            if key == "email":
                email = body[key].lower()
                if not check_email(email):
                    return jsonify({"message": "Email format is invalid"}), 400
                setattr(user, key, email)
            elif key == "password":
                if len(body[key]) < 6:
                    return jsonify({"message": "Password must be at least 6 characters"}), 400
                bpassword = bytes(body[key], "utf-8")
                salt = bcrypt.gensalt(14)
                hashed_password = bcrypt.hashpw(password=bpassword, salt=salt)
                setattr(user, key, hashed_password)
            elif isinstance(body[key], int) or isinstance(body[key], float):
                    setattr(user, key, body[key])
            else:
                setattr(user, key, body[key].capitalize())
    db.session.commit()
    return jsonify({"message": "A user has been updated", "email": user.email}), 201

@users.route("/user/<int:user_id>", methods=["DELETE"])
@jwt_required()
def deleteUser(user_id):
    """Dado la información necesaria elimina
    un usuario. 
    
    Esta ruta requiere autenticación para 
    retornar la información.
    """
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": user.email + " has been deleted"}), 200
    return jsonify({"message": "User not found"}), 404


@users.route("/token", methods=["POST"])
def create_token():
    """Dado la información necesaria retorna un
    token que permite autenticar al usuario. 
    """
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if email is None or password is None or email == "" or password == "":
        return {"message": "Parameters missing"}, 400
    user = User.query.filter_by(email=email.lower()).one_or_none()
    if user is None:
        return {"message": "User doesn't exist"}, 400
    password_byte = bytes(password, "utf-8")
    if bcrypt.checkpw(password_byte, user.password.encode("utf-8")):
        return {
            "message": "Token created",
            "token": create_access_token(identity=user.email),
        }, 200
    return {"message": "Incorrect password"}, 401