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
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    used = db.Column(db.Boolean, default=False)


class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, unique=True)
    prediction = db.Column(db.Boolean, default=False)


class LabTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sample_date = db.Column(db.Date, nullable=False)
    analysis_date = db.Column(db.Date)
    location = db.Column(db.String(100), default="Nahal Kofer")
    ph = db.Column(db.Integer)
    ph_2 = db.Column(db.Integer)
    ph_average = db.Column(db.Integer)
    ntu = db.Column(db.Integer)
    ntu_2 = db.Column(db.Integer)
    ave = db.Column(db.Integer)
    hardness = db.Column(db.Integer)
    ts_mg = db.Column(db.Integer)
    ts_mg_2 = db.Column(db.Integer)
    ave_ts = db.Column(db.Integer)
    ts_smg = db.Column(db.Integer)
    ts_smg_2 = db.Column(db.Integer)
    ave_tss = db.Column(db.Integer)
    fs_smg = db.Column(db.Integer)
    fs_smg_2 = db.Column(db.Integer)
    ave_fss = db.Column(db.Integer)
    vs_smg = db.Column(db.Integer)
    vs_smg_2 = db.Column(db.Integer)
    ave_vss = db.Column(db.Integer)
    td_smg = db.Column(db.Integer)
    td_smg_2 = db.Column(db.Integer)
    ave_tds = db.Column(db.Integer)
    tp_mg = db.Column(db.Integer)
    tp_mg_2 = db.Column(db.Integer)
    ave_tp = db.Column(db.Integer)
    tn = db.Column(db.Integer)
    tn_2 = db.Column(db.Integer)
    ave_tn = db.Column(db.Integer)
    cod = db.Column(db.Integer)
    cod_2 = db.Column(db.Integer)
    ave_cod = db.Column(db.Integer)
    nh4 = db.Column(db.Integer)
    nh4_2 = db.Column(db.Integer)
    ave_nh4 = db.Column(db.Integer)
    po4p = db.Column(db.Integer)
    po4p_2 = db.Column(db.Integer)
    ave_po4 = db.Column(db.Integer)
    no2 = db.Column(db.Integer)
    no2_2 = db.Column(db.Integer)
    ave_no2 = db.Column(db.Integer)
    no3 = db.Column(db.Integer)
    no3_2 = db.Column(db.Integer)
    ave_no3 = db.Column(db.Integer)
    bod = db.Column(db.Boolean)
    bod2 = db.Column(db.Boolean)
