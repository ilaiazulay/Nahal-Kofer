import base64
from io import BytesIO

import qrcode
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from website.mqtt_client import get_sensor_reading
import numpy as np
from scipy.stats import pearsonr
from . import db
from datetime import datetime, time, timedelta
import json
from excel_handler import validate_excel_file, extract_excel_file
from .models import LabTest, QRCode, Prediction
from .QR_code_functions import generate_qr_code


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    print(current_user.category)

    ph_sum = db.session.query(func.sum(LabTest.ph)).scalar()
    ph_count = db.session.query(func.count(LabTest.ph)).scalar()
    ph_average = ph_sum / ph_count if ph_sum is not None and ph_count != 0 else 0

    hardness_sum = db.session.query(func.sum(LabTest.hardness)).scalar()
    hardness_count = db.session.query(func.count(LabTest.hardness)).scalar()
    hardness_average = hardness_sum / hardness_count if hardness_sum is not None and hardness_count != 0 else 0

    ts_sum = db.session.query(func.sum(LabTest.ts_mg)).scalar()
    ts_count = db.session.query(func.count(LabTest.ts_mg)).scalar()
    ts_average = ts_sum / ts_count if ts_sum is not None and ts_count != 0 else 0

    last_two_tests = LabTest.query.order_by(desc(LabTest.sample_date)).limit(2).all()
    last_two_ph_values = [test.ph for test in last_two_tests if test.ph is not None]
    last_two_hardness_values = [test.hardness for test in last_two_tests if test.hardness is not None]
    last_two_ts_values = [test.ts_mg for test in last_two_tests if test.ts_mg is not None]

    last_two_ph_average = sum(last_two_ph_values) / len(last_two_ph_values) if last_two_ph_values else 0
    last_two_hardness_average = sum(last_two_hardness_values) / len(last_two_hardness_values) if last_two_hardness_values else 0
    last_two_ts_average = sum(last_two_ts_values) / len(last_two_ts_values) if last_two_ts_values else 0

    current_reading = get_sensor_reading()
    current_reading = json.loads(current_reading)
    if not current_reading:
        current_reading = 0
    else:
        current_reading = int(current_reading["distance"])
    print(get_sensor_reading())
    today = datetime.utcnow()
    future_date = today + timedelta(days=5)

    # Query for any flood predictions within the next 5 days
    flood_prediction = Prediction.query.filter(
        Prediction.date >= today,
        Prediction.date <= future_date,
        Prediction.prediction == True
    ).first()  # Get the first result if exists

    if flood_prediction:
        print(f"Flood predicted on {flood_prediction.date.strftime('%Y-%m-%d')}")
        flood_prediction_alert = f"Flood alert for {flood_prediction.date.strftime('%Y-%m-%d')}!"
        color = 'red'
    else:
        print("No flood predicted in the next 5 days.")
        flood_prediction_alert = "No flood alert for the upcoming week."
        color = 'green'

    return render_template("home.html", user=current_user, ph_average=ph_average, hardness_average=hardness_average,
                           ts_average=ts_average, last_two_ph_average=last_two_ph_average,
                           last_two_hardness_average=last_two_hardness_average, last_two_ts_average=last_two_ts_average,
                           distance=current_reading, flood_prediction_alert=flood_prediction_alert, color=color)


@views.route('/upload_file', methods=['GET', 'POST'])
@login_required
def upload_file():
    if current_user.category == 'Lab':
        response_status = 0  # Initialize the response variable
        response = ''

        if request.method == 'POST':
            file = request.files.get('excel_file')  # Access the uploaded Excel file
            print(file)
            if not file:
                response = {
                    "message": 'No file provided',
                    "status": 'failed'
                }
                response_status = 400
                print(1)
            elif file.filename == '':
                response = {
                    "message": 'No file selected',
                    "status": 'failed'
                }
                response_status = 400
                print(2)
            else:
                print(f"Received file: {file.filename}")
                if validate_excel_file(file) and extract_excel_file(file):
                    response = {
                        "message": 'File is valid',
                        "status": 'success'
                    }
                    response_status = 200
                    print(3)
                else:
                    response = {
                        "message": 'Invalid Excel file',
                        "status": 'failed'
                    }
                    response_status = 400
                    print(4)
        return render_template("upload_file.html", user=current_user, response=response, response_status=response_status)
    else:
        return render_template("home.html", user=current_user)


# @views.route('/delete-shift', methods=['POST'])
# @login_required
# def delete_shift():
#     shift = json.loads(request.data)
#     shift_id = shift['shiftId']
#     shift = Shift.query.get(shift_id)
#     if shift:
#         if shift.user_id == current_user.id:
#             db.session.delete(shift)
#             db.session.commit()
#
#     return jsonify({})

@views.route('/lab_tests', methods=['GET', 'POST'])
@login_required
def lab_tests():
    start_time = None
    finish_time = None
    lab_tests = LabTest.query.all()
    print(lab_tests)

    if request.method == 'POST':
        string_start_time = request.form.get('start_time')
        string_finish_time = request.form.get('finish_time')

        try:
            start_time = datetime.strptime(string_start_time, '%Y-%m-%d').date()
            finish_time = datetime.strptime(string_finish_time, '%Y-%m-%d').date()

            if start_time >= finish_time:
                flash('Start of the shift can not be after or the same as the end of the shift', category='error')
                return render_template("lab_tests.html", user=current_user, start_time=start_time,
                                       finish_time=finish_time, lab_tests=lab_tests)
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', category='error')
            return render_template("lab_tests.html", user=current_user, start_time=start_time,
                                   finish_time=finish_time, lab_tests=lab_tests)

    return render_template("lab_tests.html", user=current_user, start_time=start_time,
                           finish_time=finish_time, lab_tests=lab_tests)


@views.route('/graphs', methods=['GET', 'POST'])
@login_required
def graphs():
    lab_tests = LabTest.query.all()

    return render_template("graphs.html", user=current_user, lab_tests=lab_tests)


@views.route('/get_graph_data', methods=['POST'])
@login_required
def get_graph_data():
    option = request.json.get('option')

    lab_tests = LabTest.query.with_entities(LabTest.sample_date, getattr(LabTest, option)).all()
    print(lab_tests)

    # Extracting data for labels and values
    labels = [str(sample) for sample, value in lab_tests]  # Use sample directly as label
    values = [value for sample, value in lab_tests]
    print(labels, values)

    return jsonify(labels=labels, values=values)


@views.route('/statistics', methods=['GET', 'POST'])
@login_required
def statistics():
    lab_tests = LabTest.query.all()

    return render_template("statistics.html", user=current_user, lab_tests=lab_tests)


@views.route('/get_correlation_graph_data', methods=['POST'])
@login_required
def get_correlation_graph_data():
    option1 = request.json.get('option1')
    option2 = request.json.get('option2')

    lab_tests1 = LabTest.query.with_entities(LabTest.sample_date, getattr(LabTest, option1)).all()
    lab_tests2 = LabTest.query.with_entities(LabTest.sample_date, getattr(LabTest, option2)).all()

    # Extracting data for labels and values
    labels = [str(sample) for sample, _ in lab_tests1]  # Use sample directly as label
    values1 = np.array([value if value is not None else np.nan for _, value in lab_tests1], dtype=float)
    values2 = np.array([value if value is not None else np.nan for _, value in lab_tests2], dtype=float)

    # Filter out indices where either array has NaN or inf values
    valid_indices = ~(np.isnan(values1) | np.isnan(values2) | np.isinf(values1) | np.isinf(values2))
    values1_clean = values1[valid_indices]
    values2_clean = values2[valid_indices]

    # Calculate correlation
    if len(values1_clean) > 1 and len(values2_clean) > 1:
        correlation, _ = pearsonr(values1_clean, values2_clean)
        correlation_message = f"Correlation: {correlation:.2f}"
    else:
        correlation_message = "Not enough data for correlation."

    print(correlation_message)

    # Convert cleaned data back to lists for JSON response
    labels_clean = [labels[i] for i in np.where(valid_indices)[0]]
    values1_clean = values1_clean.tolist()
    values2_clean = values2_clean.tolist()

    return jsonify(labels=labels_clean, values1=values1_clean, values2=values2_clean, correlation=correlation_message)


@views.route('/sensor')
@login_required
def sensor():
    current_reading = get_sensor_reading()
    current_reading = json.loads(current_reading)
    current_reading = int(current_reading["distance"])
    flood_alert = ""
    if current_reading <= 27:
        flood_alert = "Water levels are high!"
    today = datetime.utcnow()
    future_date = today + timedelta(days=5)

    # Query for any flood predictions within the next 5 days
    flood_prediction = Prediction.query.filter(
        Prediction.date >= today,
        Prediction.date <= future_date,
        Prediction.prediction == True
    ).first()  # Get the first result if exists

    if flood_prediction:
        print(f"Flood predicted on {flood_prediction.date.strftime('%Y-%m-%d')}")
        flood_prediction_alert = f"Flood alert for {flood_prediction.date.strftime('%Y-%m-%d')}!"
        color = 'red'
    else:
        print("No flood predicted in the next 5 days.")
        flood_prediction_alert = "No flood alert for the upcoming week."
        color = 'green'

    return render_template('sensor.html', user=current_user, distance=current_reading, flood_alert=flood_alert, flood_prediction_alert=flood_prediction_alert, color=color)


@views.route('/get_sensor_data')
def get_sensor_data():
    current_reading = get_sensor_reading()
    print(current_reading)
    return current_reading


@views.route('/submit_test', methods=['GET', 'POST'])
@login_required
def add_test():
    if current_user.category == 'Lab':

        code = request.args.get('code')
        name = request.args.get('name')
        qr_created_time = request.args.get('qr_created_time')
        latitude = request.args.get('lat')
        longitude = request.args.get('lon')
        qr_exists = False  # No QR code found with that code

        if code and name and qr_created_time and latitude and longitude:
            qr_created_date = datetime.strptime(qr_created_time, "%Y-%m-%dT%H:%M:%S.%f").date()
            qr_record = QRCode.query.filter_by(code=code).first()
            if qr_record:
                qr_exists = True  # The QR code exists

        if request.method == 'GET':
            qr_record = QRCode.query.filter_by(code=code).first()
            if qr_record and qr_record.used is False:
                location = str(latitude) + "," + str(longitude)
                print(location, qr_created_time)
                return render_template('submit_test.html', date=qr_created_date, location=location, name=current_user.first_name, user=current_user)
            if qr_record and qr_record.used:
                return redirect(url_for('views.home'))

        if request.method == 'POST':
            # Extract form data
            date_format = "%Y-%m-%d"
            sample_date = request.form.get('sampleDate')
            sample_date = datetime.strptime(sample_date, date_format)
            print(type(sample_date))
            analysis_date = request.form.get('analysisDate', None)
            if analysis_date is None:
                # If analysis date is not provided, use the current date
                analysis_date = datetime.now().strftime('%Y-%m-%d')
            else:
                analysis_date = datetime.strptime(analysis_date, date_format)
            ph = request.form.get('ph', None)
            ph2 = request.form.get('ph2', None)
            ph_avg = request.form.get('phAvg', None)
            ntu = request.form.get('ntu', None)
            ntu2 = request.form.get('ntu2', None)
            ave_ntu = request.form.get('aveNtu', None)
            hardness = request.form.get('hardness', None)
            ts_mg = request.form.get('tsMg', None)
            ts_mg2 = request.form.get('tsMg2', None)
            ave_ts = request.form.get('aveTs', None)
            ts_smg = request.form.get('tsSmg', None)
            ts_smg2 = request.form.get('tsSmg2', None)
            ave_tss = request.form.get('aveTss', None)
            fs_smg = request.form.get('fsSmg', None)
            fs_smg2 = request.form.get('fsSmg2', None)
            ave_fss = request.form.get('aveFss', None)
            vs_smg = request.form.get('vsSmg', None)
            vs_smg2 = request.form.get('vsSmg2', None)
            ave_vss = request.form.get('aveVss', None)
            td_smg = request.form.get('tdSmg', None)
            td_smg2 = request.form.get('tdSmg2', None)
            ave_tds = request.form.get('aveTds', None)
            tp_mg = request.form.get('tpMg', None)
            tp_mg2 = request.form.get('tpMg2', None)
            ave_tp = request.form.get('aveTp', None)
            tn = request.form.get('tn', None)
            tn2 = request.form.get('tn2', None)
            ave_tn = request.form.get('aveTn', None)
            cod = request.form.get('cod', None)
            cod2 = request.form.get('cod2', None)
            ave_cod = request.form.get('aveCod', None)
            nh4 = request.form.get('nh4', None)
            nh42 = request.form.get('nh42', None)
            ave_nh4 = request.form.get('aveNh4', None)
            po4p = request.form.get('po4p', None)
            po4p2 = request.form.get('po4p2', None)
            ave_po4 = request.form.get('avePo4', None)
            no2 = request.form.get('no2', None)
            no22 = request.form.get('no22', None)
            ave_no2 = request.form.get('aveNo2', None)
            no3 = request.form.get('no3', None)
            no32 = request.form.get('no32', None)
            ave_no3 = request.form.get('aveNo3', None)
            bod = request.form.get('bod', None)
            if bod:
                bod = True
            else:
                bod = False
            bod2 = request.form.get('bod2', None)
            if bod2:
                bod2 = True
            else:
                bod2 = False

            # Create a new LabTest object
            lab_test = LabTest(
                sample_date=sample_date,
                analysis_date=analysis_date,
                ph=ph,
                ph_2=ph2,
                ph_average=ph_avg,
                ntu=ntu,
                ntu_2=ntu2,
                ave=ave_ntu,
                hardness=hardness,
                ts_mg=ts_mg,
                ts_mg_2=ts_mg2,
                ave_ts=ave_ts,
                ts_smg=ts_smg,
                ts_smg_2=ts_smg2,
                ave_tss=ave_tss,
                fs_smg=fs_smg,
                fs_smg_2=fs_smg2,
                ave_fss=ave_fss,
                vs_smg=vs_smg,
                vs_smg_2=vs_smg2,
                ave_vss=ave_vss,
                td_smg=td_smg,
                td_smg_2=td_smg2,
                ave_tds=ave_tds,
                tp_mg=tp_mg,
                tp_mg_2=tp_mg2,
                ave_tp=ave_tp,
                tn=tn,
                tn_2=tn2,
                ave_tn=ave_tn,
                cod=cod,
                cod_2=cod2,
                ave_cod=ave_cod,
                nh4=nh4,
                nh4_2=nh42,
                ave_nh4=ave_nh4,
                po4p=po4p,
                po4p_2=po4p2,
                ave_po4=ave_po4,
                no2=no2,
                no2_2=no22,
                ave_no2=ave_no2,
                no3=no3,
                no3_2=no32,
                ave_no3=ave_no3,
                bod=bod,
                bod2=bod2,
                # Add other fields similarly
            )

            # Save the LabTest object to the database
            db.session.add(lab_test)
            db.session.commit()

            qr_record.used = True
            db.session.commit()
        return render_template('submit_test.html', user=current_user)
    else:
        return render_template('home.html', user=current_user)


@views.route('/display_qr', methods=['POST', 'GET'])
def display_qr():
    if request.method == 'POST':
        if current_user.category != 'Lab':
            flash("Unauthorized access.", "error")
            return redirect(url_for('home.html'))

        latitude = request.form.get('lat')
        longitude = request.form.get('lon')
        if not latitude or not longitude:
            flash("Latitude or longitude not provided.", "error")
            return render_template('generate_qr_code.html')

        # Assuming generate_qr_code returns a base64-encoded QR code image
        img_data = generate_qr_code(latitude, longitude, current_user.first_name)
        return render_template('display_qr.html', user=current_user, img_data=img_data)

    # Handle GET request if necessary
    return render_template('display_qr.html')


@views.route('/generate_qr_code')
def get_qr_code():
    if current_user.category == 'Lab':
        print()
        return render_template('generate_qr_code.html', user=current_user)
    else:
        return render_template('home.html', user=current_user)


