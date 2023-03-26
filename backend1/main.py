"""This simple CRUD application performs the following operations sequentially:
    1. Creates 100 new accounts with randomly generated IDs and randomly-computed balance amounts.
    2. Chooses two accounts at random and takes half of the money from the first and deposits it
     into the second.
    3. Chooses five accounts at random and deletes them.
"""

from math import floor
import os
import random
import uuid

from flask import request, jsonify, abort
from flask_login import current_user, login_user, logout_user, login_required

from models import app, db, login_manager
from models import User


# The code below inserts new accounts.
with app.app_context():
    db.create_all()

@app.route('/')
def hello_world():
    return 'Welcome to EmConnect!'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/api/get_users', methods=['GET'])
# @login_required
def get_users():
    return jsonify([{
        'id':user.id, 'name':user.name, 'email':user.email, 'publicKey' : user.publicKey, 'privateKey':user.privateKey
    } for user in User.query.all()
    ])


@app.route('/api/signup', methods=['POST'])
def signup():
    id = str(uuid.uuid4())
    email = request.json.get('email')
    name = request.json.get('name')
    password = request.json.get('password')
    publicKey = request.json.get('publicKey')
    privateKey = request.json.get('privateKey')

    if not email or not password:
        return jsonify(status='failure', message='Missing email or password')

    if User.query.filter_by(email=email).count():
        return jsonify(status='failure', message='User with email already exists')

    user = User(id=id,email=email, name=name,password=password,publicKey=publicKey, privateKey=privateKey)
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=True)

    return jsonify(
        status='success',
        user=current_user.to_json()
    )

@app.route("/api/get_id/<user_id>", methods=["GET"])
def getUserName(user_id):
    # User.query.get(user_id)
    user = User.query.get(user_id)

    return jsonify(
        {'name':user.name}
    )


    # target_user = User.query.filter_by(id=user_id).first()
    # return jsonify(target_user)

@app.route('/api/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
       return "Please enter password"

    user = User.query.filter_by(email=email).first()

    if user is None:
        abort(401)

    if user and user.verify_password(password):
        login_user(user, remember=True)
    else:
        abort(401)

    return jsonify(
        status='success',
        user=current_user.to_json()
    )

if __name__ == '__main__':
    app.run(port=3000)
