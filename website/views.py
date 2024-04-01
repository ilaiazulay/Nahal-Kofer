from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from website.mqtt_client import get_sensor_reading
import numpy as np
from scipy.stats import pearsonr
from . import db
from datetime import datetime, time
import json
from excel_handler import validate_excel_file, extract_excel_file
from .models import LabTest

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    print(current_user)

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

    return render_template("home.html", user=current_user, ph_average=ph_average, hardness_average=hardness_average,
                           ts_average=ts_average, last_two_ph_average=last_two_ph_average,
                           last_two_hardness_average=last_two_hardness_average, last_two_ts_average=last_two_ts_average)


@views.route('/upload_file', methods=['GET', 'POST'])
@login_required
def upload_file():
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
    print(lab_tests1)

    # Extracting data for labels and values
    labels = [str(sample) for sample, value in lab_tests1]  # Use sample directly as label
    values1 = [value for sample, value in lab_tests1]
    values2 = [value for sample, value in lab_tests2]

    return jsonify(labels=labels, values1=values1, values2=values2)


@views.route('/get_correlation_data', methods=['POST'])
@login_required
def get_correlation_data():
    option1 = request.json.get('option1')
    option2 = request.json.get('option2')

    lab_tests1 = LabTest.query.with_entities(LabTest.sample_date, getattr(LabTest, option1)).all()
    lab_tests2 = LabTest.query.with_entities(LabTest.sample_date, getattr(LabTest, option2)).all()

    # Extracting data for labels and values
    labels = [str(sample) for sample, _ in lab_tests1]  # Use sample directly as label
    values1 = np.array([value for _, value in lab_tests1], dtype=float)
    values2 = np.array([value for _, value in lab_tests2], dtype=float)

    # Remove NaN and inf values from both arrays
    valid_indices = ~(np.isnan(values1) | np.isnan(values2) | np.isinf(values1) | np.isinf(values2))
    values1 = values1[valid_indices]
    values2 = values2[valid_indices]

    # Calculate correlation
    correlation = np.nan  # Default value for correlation in case calculation fails
    if len(values1) > 1 and len(values2) > 1:
        correlation, _ = pearsonr(values1, values2)
        if np.isnan(correlation):
            correlation = None  # Replace NaN with a default value

    print(correlation)

    return jsonify(correlation=correlation)


@views.route('/sensor')
@login_required
def sensor():
    current_reading = get_sensor_reading()
    print(current_reading)
    return render_template('sensor.html', user=current_user, distance=current_reading)


@views.route('/get_sensor_data')
def get_sensor_data():
    current_reading = get_sensor_reading()
    print(current_reading)
    return jsonify({'distance': current_reading})

