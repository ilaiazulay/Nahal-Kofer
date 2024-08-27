import json
from datetime import datetime, timedelta
import requests
from sqlalchemy import desc


def setup_scheduler(app):
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.start()

    # Pass the app instance directly to the jobs
    scheduler.add_job(lambda: save_daily_sensor_reading(app), 'cron', hour=11, minute=55, second=0)
    scheduler.add_job(lambda: check_flood_risk(app), 'cron', hour=13, minute=59, second=0)
    scheduler.add_job(id='Sensor Reading Task', func=lambda: get_water_level_alert(app), trigger='interval', seconds=10)

    @app.teardown_appcontext
    def shutdown_scheduler(exception=None):
        if scheduler.running:
            scheduler.shutdown(wait=False)  # Change here to not wait for jobs to complete


def check_flood_risk(app):
    with app.app_context():
        from website import db
        from website.models import Prediction
        # Print the risk of flooding for the next five days
        print("Checking flood risk for the next 5 days:")
        for i in range(5):
            target_date = datetime.utcnow().date() + timedelta(days=i)
            try:
                water_level_distance = get_water_level()
                water_opacity = get_water_opacity()
                expected_precipitation = get_expected_precipitation(target_date)

                # Convert precipitation prediction from string to float
                predicted_precip_cm = float(expected_precipitation.split(": ")[1].split(" ")[0])
                print(water_level_distance, water_opacity, predicted_precip_cm)

                data = {
                    'water_level_distance': water_level_distance,
                    'water_opacity': water_opacity,
                    'precipitation': predicted_precip_cm
                }

                # Assuming the flood prediction service expects the precipitation in cm
                response = requests.post('http://localhost:8000/predict', json=data)
                response_data = response.json()
                prediction_result = bool(response_data['prediction'])
                print(f"Flood risk for {target_date.strftime('%Y-%m-%d')}: {response_data['prediction']} (1 indicates potential flood)")

                # Save the prediction to the database
                new_prediction = Prediction(date=target_date, prediction=prediction_result)
                db.session.add(new_prediction)
                db.session.commit()

            except Exception as e:
                print(f"Failed to get flood risk prediction for {target_date.strftime('%Y-%m-%d')}: {e}")


def get_water_level():
    from website.models import Sensor
    # Assuming 'water level' is the type used for water level sensors
    latest_water_level = Sensor.query.filter_by(type='distance').order_by(desc(Sensor.date)).first()
    if latest_water_level:
        return latest_water_level.value
    else:
        return None  # Handle the case where no water level data is available


def get_water_opacity():
    from website.models import LabTest
    # Fetch the most recent LabTest where ntu is not null
    latest_lab_test = LabTest.query.filter(LabTest.ntu.isnot(None)).order_by(desc(LabTest.sample_date)).first()
    if latest_lab_test:
        return float(latest_lab_test.ntu)
    else:
        return None  # Handle the case where no non-null ntu records exist


def get_expected_precipitation(target_date):
    lat, lon = 32.068424, 34.824783  # Coordinates for Tel Aviv
    api_key = "87a8064c9b4357fcf99ad406e6e63f02"  # Your OpenWeatherMap API key
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


def save_daily_sensor_reading(app):
    print("save daily sensor")
    from website import db
    with app.app_context():  # Use the passed app instance for the application context
        from .models import Sensor
        from website.views.views import get_distance_sensor_data
        try:
            sensor_data = get_distance_sensor_data()
            sensor_dict = json.loads(sensor_data)
            sensor_value = float(sensor_dict['distance'])

            new_sensor_reading = Sensor(type='distance', value=sensor_value)
            db.session.add(new_sensor_reading)
            db.session.commit()
            print("Saved daily sensor reading:", new_sensor_reading.value)
        except Exception as e:
            print("Failed to save daily sensor reading:", e)


def get_water_level_alert(app):
    print("get_water_level_alert")
    from .models import User
    with app.app_context():  # Use the passed app instance for the application context
        from website.services.mqtt_client import get_distance_reading
        sensor_reading = get_distance_reading()
        sensor_reading = json.loads(sensor_reading)
        if not sensor_reading:
            sensor_reading = 0
        else:
            sensor_reading = int(sensor_reading["distance"])
        if sensor_reading <= 27:
            # Select only users with category 'Municipality'
            municipality_users = User.query.filter_by(category='Municipality').all()
            now = datetime.utcnow()

            for user in municipality_users:
                # Check if the user was never emailed or if it's been more than a day since the last email
                if user.last_email_sent is None or now - user.last_email_sent > timedelta(days=1):
                    send_alert_email(user, sensor_reading, now)


def send_alert_email(user, current_reading, now):
    from website import Message, mail, db
    try:
        msg = Message("High Water Level Alert",
                      sender=os.getenv("EMAIL_USERNAME"),  # Ensure this is set in your environment variables
                      recipients=[user.email])
        msg.body = f"Dear {user.first_name}, water levels are high at {current_reading} cm!"
        mail.send(msg)
        user.last_email_sent = now  # Update the last email sent timestamp
        db.session.commit()
        print(f"Email sent to {user.email} due to high water level.")
    except Exception as e:
        print(f"Failed to send email to {user.email}: {e}")
