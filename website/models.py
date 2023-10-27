from . import db
from flask_login import UserMixin


class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.column(db.DateTime(timezone=True))
    start = db.column(db.Integer)
    finish = db.column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    base_wage = db.Column(db.Integer)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    shifts = db.relationship('Shift')
