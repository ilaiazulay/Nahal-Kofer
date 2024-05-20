import json
import os
import time
import threading
from datetime import datetime, timedelta
from website import create_app, setup_scheduler

app = create_app()
setup_scheduler(app)

def get_water_level_alert():
    with app.app_context():
        from website.models import Sensor, User
        from website.mqtt_client import get_distance_reading
        print("Running get_water_level_alert")
        try:
            sensor_reading = get_distance_reading()
            print(sensor_reading)
            sensor_reading = json.loads(sensor_reading)
            if not sensor_reading:
                sensor_reading = 100  # Default high value to avoid false alerts if sensor fails
            else:
                sensor_reading = int(sensor_reading["distance"])

            print(f"Processed sensor reading: {sensor_reading}")

            if sensor_reading <= 27:
                now = datetime.utcnow()
                print("Alert condition met, processing alerts.")
                municipality_users = User.query.filter_by(category='Municipality').all()

                for user in municipality_users:
                    if user.last_email_sent is None or now - user.last_email_sent > timedelta(days=1):
                        send_alert_email(user, sensor_reading, now)

        except Exception as e:
            print(f"Error in get_water_level_alert: {e}")


def send_alert_email(user, current_reading, now):
    from website import Message, mail, db
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

def schedule_task(interval):
    next_run = datetime.now()
    while True:
        time.sleep(max(0, (next_run - datetime.now()).total_seconds()))
        get_water_level_alert()
        next_run += timedelta(seconds=interval)

def run_scheduler():
    # Run the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=schedule_task, args=(10,))
    scheduler_thread.start()

if __name__ == '__main__':
    run_scheduler()
    app.run(debug=True)
