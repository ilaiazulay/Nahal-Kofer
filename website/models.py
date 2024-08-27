from . import db
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    category = db.Column(db.String(16))
    last_email_sent = db.Column(db.DateTime, default=datetime(2000, 1, 1))


class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(150), nullable=False)
    value = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class QRCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(256), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(100), nullable=False)
    lab_test_id = db.Column(db.Integer, db.ForeignKey('lab_test.id'))
    lab_test = db.relationship('LabTest', backref='qr_code', uselist=False)


class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, unique=True)
    prediction = db.Column(db.Boolean, default=False)
    water_level_distance = db.Column(db.Float, nullable=True)
    water_opacity = db.Column(db.Float, nullable=True)
    precipitation = db.Column(db.Float, nullable=True)




class LabTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100))
    name = db.Column(db.String(100), nullable=True)
    sample_date = db.Column(db.Date, nullable=True)
    analysis_date = db.Column(db.Date, nullable=True)
    ph = db.Column(db.Integer, nullable=True)
    ph_2 = db.Column(db.Integer, nullable=True)
    ph_average = db.Column(db.Integer, nullable=True)
    Alkalinity = db.Column(db.Integer, nullable=True)
    ntu = db.Column(db.Integer, nullable=True)
    ntu_2 = db.Column(db.Integer, nullable=True)
    ave = db.Column(db.Integer, nullable=True)
    hardness = db.Column(db.Integer, nullable=True)
    ts_mg = db.Column(db.Integer, nullable=True)
    ts_mg_2 = db.Column(db.Integer, nullable=True)
    ave_ts = db.Column(db.Integer, nullable=True)
    ts_smg = db.Column(db.Integer, nullable=True)
    ts_smg_2 = db.Column(db.Integer, nullable=True)
    ave_tss = db.Column(db.Integer, nullable=True)
    fs_smg = db.Column(db.Integer, nullable=True)
    fs_smg_2 = db.Column(db.Integer, nullable=True)
    ave_fss = db.Column(db.Integer, nullable=True)
    vs_smg = db.Column(db.Integer, nullable=True)
    vs_smg_2 = db.Column(db.Integer, nullable=True)
    ave_vss = db.Column(db.Integer, nullable=True)
    td_smg = db.Column(db.Integer, nullable=True)
    td_smg_2 = db.Column(db.Integer, nullable=True)
    ave_tds = db.Column(db.Integer, nullable=True)
    tp_mg = db.Column(db.Integer, nullable=True)
    tp_mg_2 = db.Column(db.Integer, nullable=True)
    ave_tp = db.Column(db.Integer, nullable=True)
    tn = db.Column(db.Integer, nullable=True)
    tn_2 = db.Column(db.Integer, nullable=True)
    ave_tn = db.Column(db.Integer, nullable=True)
    cod = db.Column(db.Integer, nullable=True)
    cod_2 = db.Column(db.Integer, nullable=True)
    ave_cod = db.Column(db.Integer, nullable=True)
    nh4 = db.Column(db.Integer, nullable=True)
    nh4_2 = db.Column(db.Integer, nullable=True)
    ave_nh4 = db.Column(db.Integer, nullable=True)
    po4p = db.Column(db.Integer, nullable=True)
    po4p_2 = db.Column(db.Integer, nullable=True)
    ave_po4 = db.Column(db.Integer, nullable=True)
    no2 = db.Column(db.Integer, nullable=True)
    no2_2 = db.Column(db.Integer, nullable=True)
    ave_no2 = db.Column(db.Integer, nullable=True)
    no3 = db.Column(db.Integer, nullable=True)
    no3_2 = db.Column(db.Integer, nullable=True)
    ave_no3 = db.Column(db.Integer, nullable=True)
    bod = db.Column(db.Boolean, nullable=True)
    bod2 = db.Column(db.Boolean, nullable=True)


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
