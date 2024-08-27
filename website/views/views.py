from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from website.services.mqtt_client import get_distance_reading, get_flow_rate_reading, get_ph_reading
import numpy as np
from scipy.stats import pearsonr
from website import db
from datetime import datetime, timedelta
import json
from website.services.excel_handler import validate_excel_file, extract_excel_file
from website.models import LabTest, QRCode, Prediction, Location, Sensor
from website.services.QR_code_functions import generate_qr_code

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    print(current_user.category)

    distance = get_distance_reading()
    distance = json.loads(distance)
    if not distance:
        distance = 0
    else:
        try:
            distance = int(distance["distance"])
        except:
            distance = 0

    flow = get_flow_rate_reading()
    flow = json.loads(flow)
    if not flow:
        flow = 0
    else:
        try:
            flow = int(flow["flow_rate"])
        except:
            flow = 0

    ph = get_ph_reading()
    try:
        ph = json.loads(ph)
        if not ph:
            ph = 7
        else:
            ph = int(ph["ph_value"])
    except (ValueError, TypeError):
        if not isinstance(ph, int):
            ph = 7

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

    return render_template("home.html", user=current_user, distance=distance, flow=flow, ph=ph,
                           flood_prediction_alert=flood_prediction_alert, color=color)


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
        return render_template("upload_file.html", user=current_user, response=response,
                               response_status=response_status)
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


@views.route('/lab_tests/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_lab_test(id):
    lab_test = LabTest.query.get_or_404(id)

    if request.method == 'POST':
        try:
            # sample_date = request.form.get('analysis_date', None)
            # if sample_date:
            #     sample_date = datetime.strptime(sample_date, '%Y-%m-%d').date()
            # analysis_date = request.form.get('analysis_date', None)
            # if analysis_date:
            #     analysis_date = datetime.strptime(analysis_date, '%Y-%m-%d').date()
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
            # Add other fields as needed

            # if sample_date is not None:
            #     lab_test.sample_date = sample_date
            # if analysis_date is not None:
            #     lab_test.analysis_date = analysis_date
            lab_test.ph = ph
            lab_test.ph_2 = ph2
            lab_test.ph_average = ph_avg
            lab_test.ntu = ntu
            lab_test.ntu_2 = ntu2
            lab_test.ave = ave_ntu
            lab_test.hardness = hardness
            lab_test.ts_mg = ts_mg
            lab_test.ts_mg_2 = ts_mg2
            lab_test.ave_ts = ave_ts
            lab_test.ts_smg = ts_smg
            lab_test.ts_smg_2 = ts_smg2
            lab_test.ave_tss = ave_tss
            lab_test.fs_smg = fs_smg
            lab_test.fs_smg_2 = fs_smg2
            lab_test.ave_fss = ave_fss
            lab_test.vs_smg = vs_smg
            lab_test.vs_smg_2 = vs_smg2
            lab_test.ave_vss = ave_vss
            lab_test.td_smg = td_smg
            lab_test.td_smg_2 = td_smg2
            lab_test.ave_tds = ave_tds
            lab_test.tp_mg = tp_mg
            lab_test.tp_mg_2 = tp_mg2
            lab_test.ave_tp = ave_tp
            lab_test.tn = tn
            lab_test.tn_2 = tn2
            lab_test.ave_tn = ave_tn
            lab_test.cod = cod
            lab_test.cod_2 = cod2
            lab_test.ave_cod = ave_cod
            lab_test.nh4 = nh4
            lab_test.nh4_2 = nh42
            lab_test.ave_nh4 = ave_nh4
            lab_test.po4p = po4p
            lab_test.po4p_2 = po4p2
            lab_test.ave_po4 = ave_po4
            lab_test.no2 = no2
            lab_test.no2_2 = no22
            lab_test.ave_no2 = ave_no2
            lab_test.no3 = no3
            lab_test.no3_2 = no32
            lab_test.ave_no3 = ave_no3
            lab_test.bod = bod
            lab_test.bod2 = bod2
            db.session.commit()
            flash('Lab test updated successfully!', category='success')
            return redirect(url_for('views.lab_tests'))
        except Exception as e:
            flash(f'Error updating lab test: {e}', category='error')

    return render_template('edit_lab_test.html', lab_test=lab_test, user=current_user)


@views.route('/lab_tests/delete/<int:id>', methods=['POST'])
@login_required
def delete_lab_test(id):
    lab_test = LabTest.query.get_or_404(id)
    db.session.delete(lab_test)
    db.session.commit()
    flash('Lab test deleted successfully!', category='success')
    return redirect(url_for('views.lab_tests'))


@views.route('/graphs/lab_tests', methods=['GET', 'POST'])
@login_required
def lab_tests_graphs():
    lab_tests = LabTest.query.all()

    return render_template("lab_tests_graphs.html", user=current_user, lab_tests=lab_tests)


@views.route('/get_graph_data', methods=['POST'])
@login_required
def get_graph_data():
    data = request.get_json()
    option = data.get('option')
    date_data = data.get('dateData', {})

    if 'year' in date_data:
        year = int(date_data['year'])
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
    elif 'startDate' in date_data and 'endDate' in date_data:
        start_date = datetime.strptime(date_data['startDate'], '%Y-%m-%d')
        end_date = datetime.strptime(date_data['endDate'], '%Y-%m-%d')
    else:
        return jsonify({"error": "Invalid date data"}), 400

    # Filter data within the time range and compute average for each location
    results = LabTest.query \
        .with_entities(LabTest.location, func.avg(getattr(LabTest, option)).label('average')) \
        .filter(LabTest.sample_date >= start_date, LabTest.sample_date <= end_date) \
        .filter(LabTest.location.in_(['Metanya Left', 'Metanya Right', 'Safari', 'National Park', 'Maccabia Bridge'])) \
        .group_by(LabTest.location) \
        .all()

    labels = [location for location, _ in results]  # Location names
    values = [round(average, 2) if average is not None else 0 for _, average in results]  # Average values, rounded
    print(values)

    return jsonify(labels=labels, values=values)


@views.route('/get_line_graph_data', methods=['POST'])
@login_required
def get_line_graph_data():
    data = request.get_json()
    option = data.get('option')
    date_data = data.get('dateData', {})

    if 'startDate' in date_data and 'endDate' in date_data:
        start_date = datetime.strptime(date_data['startDate'], '%Y-%m-%d')
        end_date = datetime.strptime(date_data['endDate'], '%Y-%m-%d')
    else:
        return jsonify({"error": "Invalid date data"}), 400

    lab_tests = LabTest.query \
        .with_entities(LabTest.sample_date, LabTest.location, getattr(LabTest, option)) \
        .filter(LabTest.sample_date >= start_date, LabTest.sample_date <= end_date) \
        .all()

    data_dict = {}
    for sample_date, location, value in lab_tests:
        if location and value is not None:  # Ensure location and value are not None
            if location not in data_dict:
                data_dict[location] = {'dates': [], 'values': []}
            data_dict[location]['dates'].append(sample_date.strftime('%Y-%m-%d'))
            data_dict[location]['values'].append(value)

    # Sort the dictionary keys
    sorted_data_dict = {k: data_dict[k] for k in sorted(data_dict.keys())}

    return jsonify(sorted_data_dict)




@views.route('/graphs/sensors', methods=['GET', 'POST'])
@login_required
def sensors_graphs():
    lab_tests = LabTest.query.all()
    sensors = Sensor.query.all()

    return render_template("sensors_graphs.html", user=current_user, lab_tests=lab_tests, sensors=sensors)


@views.route('/get_sensors_graph_data', methods=['POST'])
@login_required
def get_sensors_graph_data():
    data = request.get_json()
    option = data.get('option')
    date_data = data.get('dateData', {})

    if 'year' in date_data:
        year = int(date_data['year'])
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
    elif 'startDate' in date_data and 'endDate' in date_data:
        start_date = datetime.strptime(date_data['startDate'], '%Y-%m-%d')
        end_date = datetime.strptime(date_data['endDate'], '%Y-%m-%d')
    else:
        return jsonify({"error": "Invalid date data"}), 400

    data_dict = {}

    if option == 'PH':
        lab_tests = LabTest.query \
            .with_entities(LabTest.sample_date, LabTest.location, LabTest.ph) \
            .filter(LabTest.sample_date >= start_date, LabTest.sample_date <= end_date) \
            .all()

        for sample_date, location, value in lab_tests:
            if location and value is not None:  # Ensure location and value are not None
                if location not in data_dict:
                    data_dict[location] = {'dates': [], 'values': []}
                data_dict[location]['dates'].append(sample_date.strftime('%Y-%m-%d'))
                data_dict[location]['values'].append(value)

    elif option == 'Water Level':
        sensors = Sensor.query \
            .with_entities(Sensor.date, Sensor.type, Sensor.value) \
            .filter(Sensor.date >= start_date, Sensor.date <= end_date, Sensor.type == 'distance') \
            .all()

        for date, type_, value in sensors:
            location = "Water Level Sensor"  # Assuming there is only one type of water level sensor
            if location and value is not None:  # Ensure location and value are not None
                if location not in data_dict:
                    data_dict[location] = {'dates': [], 'values': []}
                data_dict[location]['dates'].append(date.strftime('%Y-%m-%d'))
                data_dict[location]['values'].append(value)

    elif option == 'Water Current':
        sensors = Sensor.query \
            .with_entities(Sensor.date, Sensor.type, Sensor.value) \
            .filter(Sensor.date >= start_date, Sensor.date <= end_date, Sensor.type == 'flow') \
            .all()

        for date, type_, value in sensors:
            location = "Water Current Sensor"  # Assuming there is only one type of water current sensor
            if location and value is not None:  # Ensure location and value are not None
                if location not in data_dict:
                    data_dict[location] = {'dates': [], 'values': []}
                data_dict[location]['dates'].append(date.strftime('%Y-%m-%d'))
                data_dict[location]['values'].append(value)

    else:
        return jsonify({"error": "Invalid option"}), 400

    # Sort the dictionary keys
    sorted_data_dict = {k: data_dict[k] for k in sorted(data_dict.keys()) if k is not None}

    return jsonify(sorted_data_dict)



@views.route('/get_min_max', methods=['POST'])
@login_required
def get_min_max():
    data = request.get_json()
    option = data.get('option')
    date_data = data.get('dateData', {})

    if 'year' in date_data:
        year = int(date_data['year'])
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
    elif 'startDate' in date_data and 'endDate' in date_data:
        start_date = datetime.strptime(date_data['startDate'], '%Y-%m-%d')
        end_date = datetime.strptime(date_data['endDate'], '%Y-%m-%d')
    else:
        return jsonify({"error": "Invalid date data"}), 400

    # Query to get min, max for each location
    results = LabTest.query \
        .with_entities(
        LabTest.location,
        func.min(getattr(LabTest, option)).label('min'),
        func.max(getattr(LabTest, option)).label('max')
    ) \
        .filter(LabTest.sample_date >= start_date, LabTest.sample_date <= end_date) \
        .filter(LabTest.location.in_(['Metanya Left', 'Metanya Right', 'Safari', 'National Park', 'Maccabia Bridge'])) \
        .group_by(LabTest.location) \
        .all()

    labels = [location for location, _, _ in results]
    mins = [round(float(min_value), 2) if min_value and min_value != '' else 0 for _, min_value, _ in results]
    maxs = [round(float(max_value), 2) if max_value and max_value != '' else 0 for _, _, max_value in results]
    print(labels, mins, maxs)

    return jsonify(labels=labels, mins=mins, maxs=maxs)


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
    current_reading = get_distance_reading()
    current_reading = json.loads(current_reading)
    current_reading = int(current_reading["distance"])

    flow_rate = get_flow_rate_reading()
    flow_rate = json.loads(flow_rate)
    flow_rate = float(flow_rate["flow_rate"])

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

    return render_template('sensor.html', user=current_user, distance=current_reading, flow_rate=flow_rate,
                           flood_alert=flood_alert, flood_prediction_alert=flood_prediction_alert, color=color)


@views.route('/get_distance_sensor_data')
def get_distance_sensor_data():
    current_reading = get_distance_reading()
    return current_reading
    # return jsonify({"distance": current_reading})


@views.route('/get_flow_sensor_data')
def get_flow_sensor_data():
    current_reading = get_flow_rate_reading()
    return current_reading
    # print(current_reading)
    # return jsonify({"flow_rate": current_reading})


@views.route('/get_ph_sensor_data')
def get_ph_sensor_data():
    current_reading = get_ph_reading()
    return current_reading
    # print(current_reading)
    # return jsonify({"flow_rate": current_reading})


@views.route('/submit_test', methods=['GET', 'POST'])
@login_required
def add_test():
    if current_user.category == 'Lab':

        locations = Location.query.all()  # Fetch all locations from the database
        code = request.args.get('code')
        name = request.args.get('name')
        qr_created_time = request.args.get('qr_created_time')
        location = request.args.get('location')
        qr_exists = False  # No QR code found with that code
        qr_record = ''

        if code and name and qr_created_time and location:
            qr_created_date = datetime.strptime(qr_created_time, "%Y-%m-%dT%H:%M:%S.%f").date()
            qr_record = QRCode.query.filter_by(code=code).first()
            if qr_record:
                qr_exists = True  # The QR code exists
                lab_test = qr_record.lab_test  # Fetch the associated lab test
                print(lab_test)

        if request.method == 'GET':
            qr_record = QRCode.query.filter_by(code=code).first()
            if qr_record:
                print(location, qr_created_time)
                return render_template('submit_test.html', location=location, name=current_user.first_name,
                                       user=current_user, lab_test=lab_test, locations=locations)
            else:
                return render_template('submit_test.html', location="", name="", user=current_user, lab_test="", locations=locations)

        if request.method == 'POST':
            # Extract form data
            date_format = "%Y-%m-%d"
            sample_date = request.form.get('sampleDate', None)
            if sample_date and sample_date != '':
                sample_date = datetime.strptime(sample_date, date_format).date()
                print(type(sample_date))
            analysis_date = request.form.get('analysisDate', None)
            if analysis_date is None or analysis_date == '':
                # If analysis date is not provided, use the current date
                analysis_date = datetime.now().date()
            else:
                analysis_date = datetime.strptime(analysis_date, date_format).date()
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

            if qr_record:
                print('here')
                print(analysis_date)
                if sample_date != '':
                    print(sample_date)
                    lab_test.sample_date = sample_date
                if analysis_date is not None:
                    lab_test.analysis_date = analysis_date
                lab_test.ph = ph
                lab_test.ph_2 = ph2
                lab_test.ph_average = ph_avg
                lab_test.ntu = ntu
                lab_test.ntu_2 = ntu2
                lab_test.ave = ave_ntu
                lab_test.hardness = hardness
                lab_test.ts_mg = ts_mg
                lab_test.ts_mg_2 = ts_mg2
                lab_test.ave_ts = ave_ts
                lab_test.ts_smg = ts_smg
                lab_test.ts_smg_2 = ts_smg2
                lab_test.ave_tss = ave_tss
                lab_test.fs_smg = fs_smg
                lab_test.fs_smg_2 = fs_smg2
                lab_test.ave_fss = ave_fss
                lab_test.vs_smg = vs_smg
                lab_test.vs_smg_2 = vs_smg2
                lab_test.ave_vss = ave_vss
                lab_test.td_smg = td_smg
                lab_test.td_smg_2 = td_smg2
                lab_test.ave_tds = ave_tds
                lab_test.tp_mg = tp_mg
                lab_test.tp_mg_2 = tp_mg2
                lab_test.ave_tp = ave_tp
                lab_test.tn = tn
                lab_test.tn_2 = tn2
                lab_test.ave_tn = ave_tn
                lab_test.cod = cod
                lab_test.cod_2 = cod2
                lab_test.ave_cod = ave_cod
                lab_test.nh4 = nh4
                lab_test.nh4_2 = nh42
                lab_test.ave_nh4 = ave_nh4
                lab_test.po4p = po4p
                lab_test.po4p_2 = po4p2
                lab_test.ave_po4 = ave_po4
                lab_test.no2 = no2
                lab_test.no2_2 = no22
                lab_test.ave_no2 = ave_no2
                lab_test.no3 = no3
                lab_test.no3_2 = no32
                lab_test.ave_no3 = ave_no3
                lab_test.bod = bod
                lab_test.bod2 = bod2
                # Add other fields similarly

                # Save the LabTest object to the database
                db.session.commit()
                flash('Changes Saved', category='success')
                return render_template('submit_test.html', location=location, name=current_user.first_name,
                                       user=current_user, lab_test=lab_test, locations=locations)
            else:
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
                flash('Changes Saved', category='success')
                return render_template('submit_test.html', user=current_user, locations=locations)
    else:
        return render_template('home.html', user=current_user)


@views.route('/display_qr', methods=['POST', 'GET'])
def display_qr():
    if request.method == 'POST':
        if current_user.category != 'Lab':
            flash("Unauthorized access.", "error")
            return redirect(url_for('home.html'))

        location = request.form.get('location')
        if not location:
            flash("Location not provided.", "error")
            return render_template('generate_qr_code.html')

        # Assuming generate_qr_code returns a base64-encoded QR code image
        img_data = generate_qr_code(location, current_user.first_name)
        current_date = datetime.utcnow().strftime('%Y-%m-%d')
        return render_template('display_qr.html', user=current_user, location=location, current_date=current_date,
                               img_data=img_data)

    # Handle GET request if necessary
    return render_template('display_qr.html')


@views.route('/generate_qr_code')
def get_qr_code():
    if current_user.category == 'Lab':
        locations = Location.query.all()  # Fetch all locations from the database
        return render_template('generate_qr_code.html', user=current_user, locations=locations)
    else:
        return render_template('home.html', user=current_user)


@views.route('/locations', methods=['GET'])
@login_required
def locations():
    locations = Location.query.all()
    return render_template("locations.html", user=current_user, locations=locations)


@views.route('/locations/add', methods=['POST'])
@login_required
def add_location():
    location_name = request.form.get('location_name')
    if location_name:
        new_location = Location(name=location_name)
        db.session.add(new_location)
        db.session.commit()
        flash('Location added successfully!', category='success')
    else:
        flash('Location name is required.', category='error')
    return redirect(url_for('views.locations'))


@views.route('/locations/edit/<int:id>', methods=['POST'])
@login_required
def edit_location(id):
    location = Location.query.get_or_404(id)
    new_name = request.form.get('location_name')
    if new_name:
        location.name = new_name
        db.session.commit()
        flash('Location updated successfully!', category='success')
    else:
        flash('Location name is required.', category='error')
    return redirect(url_for('views.locations'))


@views.route('/locations/delete/<int:id>', methods=['POST'])
@login_required
def delete_location(id):
    location = Location.query.get_or_404(id)
    db.session.delete(location)
    db.session.commit()
    flash('Location deleted successfully!', category='success')
    return redirect(url_for('views.locations'))
