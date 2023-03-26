from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_cors import CORS
import uuid

print(uuid.uuid4)

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL'].replace("postgresql://", "cockroachdb://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(db.Model, UserMixin):
    __tablename__= 'user'
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True, index=True)
    name = db.Column(db.String)
    password = db.Column(db.String)
    publicKey = db.Column(db.String)
    privateKey = db.Column(db.String)
    def __init__(self,id, password, name, email, publicKey, privateKey):
        self.id = id
        self.password = generate_password_hash(password)
        self.name = name
        self.email = email
        self.publicKey = generate_password_hash(publicKey)
        self.privateKey = generate_password_hash(privateKey)

    
    def __repr__(self):
        return f'<User {self.name}>'

    def verify_password(self, pwd):
        return check_password_hash(self.password, pwd)
    
    def to_json(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'password': self.password,
            'publicKey': self.publicKey,
            'privateKey': self.privateKey
        }
