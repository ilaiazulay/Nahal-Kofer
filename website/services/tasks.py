import os
import time
import json
import requests
from datetime import datetime, timedelta
import threading
from sqlalchemy import desc
from website import mail, db
from website.models import Sensor, LabTest, Prediction, User
from flask_mail import Message
from flask import current_app as app


def get_water_level_alert():
    with app.app_context():
        from website.services.mqtt_client import get_distance_reading
        try:
            sensor_reading = get_distance_reading()
            print(sensor_reading)
            sensor_reading = json.loads(sensor_reading)
            if not sensor_reading:
                sensor_reading = 100  # Default high value to avoid false alerts if sensor fails
            else:
                sensor_reading = int(sensor_reading["distance"])

            if sensor_reading <= 27:  # the sensor is 20 cm above the water surface
                now = datetime.utcnow()
                print("Alert condition met, processing alerts.")
                municipality_users = User.query.filter_by(category='Municipality').all()

                for user in municipality_users:
                    if user.last_email_sent is None or now - user.last_email_sent > timedelta(days=1):
                        send_alert_email(user, sensor_reading, now)

        except Exception as e:
            print(f"Error in get_water_level_alert: {e}")


def send_alert_email(user, current_reading, now):
    try:
        if current_reading - 20 <= 0:
            current_reading = 0
        msg = Message("High Water Level Alert",
                      sender=os.getenv("EMAIL_USERNAME"),  # Ensure this is set in your environment variables
                      recipients=[user.email])
        msg.body = f"Dear {user.first_name}, water levels are high!"
        mail.send(msg)
        user.last_email_sent = now  # Update the last email sent timestamp
        db.session.commit()
        print(f"Email sent to {user.email} due to high water level.")
    except Exception as e:
        print(f"Failed to send email to {user.email}: {e}")


def schedule_task(app, interval, task_function):
    next_run = datetime.now()
    while True:
        time.sleep(max(0, (next_run - datetime.now()).total_seconds())) # first happens now then the next interval

        with app.app_context():
            task_function()

        next_run += timedelta(seconds=interval)


def run_scheduler(app):
    # Run the water level alert scheduler in a separate thread
    scheduler_thread = threading.Thread(target=schedule_task, args=(app, 10, get_water_level_alert))
    scheduler_thread.start()

    # Run the save daily sensor reading scheduler in a separate thread
    daily_interval = 24 * 60 * 60  # 24 hours in seconds
    save_sensor_thread = threading.Thread(target=schedule_task, args=(app, daily_interval, save_daily_sensor_reading))
    save_sensor_thread.start()

    # Run the check flood risk scheduler in a separate thread with a daily interval
    check_flood_thread = threading.Thread(target=schedule_task, args=(app, daily_interval, check_flood_risk))
    check_flood_thread.start()


def save_daily_sensor_reading():
    print("Running daily sensor saving")
    with app.app_context():  # Use the passed app instance for the application context
        from website.views.views import get_distance_sensor_data, get_flow_sensor_data, get_ph_sensor_data

        current_date = datetime.utcnow().date()

        try:
            # Fetch and parse distance data
            distance_data = json.loads(get_distance_sensor_data())
            distance_value = float(distance_data["distance"])
            if distance_value in [0, 1000]:
                print("Invalid distance value, not saving to database.")
            else:
                new_sensor_reading = Sensor(type='distance', value=distance_value)
                db.session.add(new_sensor_reading)
                db.session.commit()
                print("Saved daily distance reading:", new_sensor_reading.value)
        except Exception as e:
            print("Failed to save daily distance reading:", e)

        try:
            # Fetch and parse flow rate data
            flow_data = json.loads(get_flow_sensor_data())
            flow_value = float(flow_data["flow_rate"])
            if flow_value in [1000]:
                print("Invalid flow rate value, not saving to database.")
            else:
                new_sensor_reading = Sensor(type='flow', value=flow_value)
                db.session.add(new_sensor_reading)
                db.session.commit()
                print("Saved daily flow reading:", new_sensor_reading.value)
        except Exception as e:
            print("Failed to save daily flow reading:", e)

        try:
            # Fetch and parse pH data
            ph_data = json.loads(get_ph_sensor_data())
            ph_value = float(ph_data["ph_value"])
            if ph_value in [0, 1000]:
                print("Invalid pH value, not saving to database.")
            else:
                new_lab_test = LabTest(
                    sample_date=current_date,
                    analysis_date=current_date,
                    ph=ph_value,
                    ph_2=ph_value,
                    ph_average=ph_value,
                    location='Main',  # Replace with actual location if available
                    name='Daily pH Test'
                )
                db.session.add(new_lab_test)
                db.session.commit()
                print("Saved daily pH reading:", new_lab_test.ph)
        except Exception as e:
            print("Failed to save daily pH reading:", e)


def check_flood_risk():
    with app.app_context():
        print("Checking flood risk for the next 5 days:")
        for i in range(5):
            target_date = datetime.utcnow().date() + timedelta(days=i)
            try:
                water_level_distance = get_water_level()
                water_opacity = get_water_opacity()
                expected_precipitation = get_expected_precipitation(target_date)
                print(expected_precipitation)

                # Convert precipitation prediction from string to float
                predicted_precip_cm = float(expected_precipitation.split(": ")[1].split(" ")[0])
                print(water_level_distance, water_opacity, predicted_precip_cm)

                data = {
                    "water_level_distance": water_level_distance,
                    "water_opacity": water_opacity,
                    "precipitation": predicted_precip_cm
                }

                # Assuming the flood prediction service expects the precipitation in cm
                response = requests.post('http://54.216.162.220:8000/predict', json=data)
                response_data = response.json()
                prediction_result = bool(response_data['prediction'])
                print(f"Flood risk for {target_date.strftime('%Y-%m-%d')}: {response_data['prediction']} (1 indicates potential flood)")

                # Save the prediction and additional data to the database
                new_prediction = Prediction(
                    date=target_date,
                    prediction=prediction_result,
                    water_level_distance=water_level_distance,
                    water_opacity=water_opacity,
                    predicted_precip_cm=predicted_precip_cm
                )
                db.session.add(new_prediction)
                db.session.commit()

            except Exception as e:
                print(f"Failed to get flood risk prediction for {target_date.strftime('%Y-%m-%d')}: {e}")


def get_water_level():
    latest_water_level = Sensor.query.filter_by(type='distance').order_by(desc(Sensor.date)).first()
    if latest_water_level:
        return latest_water_level.value
    else:
        return None  # Handle the case where no water level data is available


def get_water_opacity():
    latest_lab_test = LabTest.query.filter(LabTest.ntu.isnot(None)).order_by(desc(LabTest.sample_date)).first()
    if latest_lab_test:
        return float(latest_lab_test.ntu)
    else:
        return None  # Handle the case where no non-null ntu records exist


def get_expected_precipitation(target_date):
    lat, lon = 32.068424, 34.824783  # Coordinates for Tel Aviv
    api_key = os.getenv("API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}"

    target_date_str = target_date.strftime('%Y-%m-%d')

    # Make the API request
    response = requests.get(url)
    data = response.json()

    total_precipitation = 0.0  # Total precipitation in mm

    # Loop through the list of forecasts
    for item in data['list']:
        forecast_time = datetime.fromtimestamp(item['dt'])
        forecast_date_str = forecast_time.strftime('%Y-%m-%d')

        # Check if the forecast is for the target date
        if forecast_date_str == target_date_str:
            # Add the precipitation for this time interval
            precipitation = item['rain'].get('3h', 0) if 'rain' in item else 0
            total_precipitation += precipitation

    # Convert mm to cm
    total_precipitation_cm = total_precipitation / 10

    return f"Predicted rain for {target_date_str}: {total_precipitation_cm:.2f} cm"

