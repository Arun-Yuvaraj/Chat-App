from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User Model"""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key= True, nullable = False)
    username = db.Column(db.String(25),nullable = False, unique = True)
    password = db.Column(db.String(), nullable = False)