from datetime import datetime
from website.models import Shift
from sqlalchemy import asc

from website import create_app  # Import your Flask application factory

# Create the Flask app
app = create_app()

# Use the app context to work within the application
with app.app_context():
    from website.models import Shift
    from sqlalchemy import asc

    # Define hourly wage rates and rules
    hourly_wage_rates = {
        20: 1.3,  # 20:00 AM to 21:00 AM (130%)
        21: 1.3,  # 21:00 AM to 22:00 AM (130%)
        22: 1.3,  # 22:00 AM to 23:00 AM (130%)
        23: 1.3,  # 23:00 PM to Midnight (130%)
        00: 1.3,  # Midnight to 01:00 AM (130%)
        1: 1.3,   # 01:00 AM to 02:00 AM (130%)
        2: 1.3,   # 02:00 AM to 03:00 AM (130%)
        3: 1.3,   # 03:00 AM to 04:00 AM (130%)
        4: 1.3,   # 04:00 AM to 05:00 AM (130%)
        5: 1.3,   # 05:00 AM to 06:00 AM (130%)

    }

    def calculate_shift_earnings(shift, hourly_wage_rates, base_wage):
        earnings = 0
        start_hour = shift.start.hour
        start_minute = shift.start.minute
        finish_hour = shift.finish.hour
        finish_minute = shift.finish.minute
        hours = 0
        extra_hours = 0

        while start_hour != finish_hour or start_minute != finish_minute:
            current_hour_rate = base_wage * (hourly_wage_rates.get(start_hour, 1.0) + extra_hours)  # Default rate is 1.0 (100%)
            if start_hour == finish_hour:
                if start_minute != finish_minute:
                    if start_minute < finish_minute:
                        minutes_worked = finish_minute - start_minute
                    else:
                        minutes_worked = 60 - finish_minute + start_minute
                earnings += current_hour_rate * minutes_worked / 60
                return earnings
            else:
                minutes_worked = 60
            earnings += current_hour_rate * minutes_worked / 60

            start_hour += 1
            hours += 1
            if hours >= 9:
                extra_hours = 0.25
            if start_hour == 24:
                start_hour = 0

            print(start_minute, finish_minute)

        return earnings


    def calculate_daily_salary(date, shifts, hourly_wage_rates):
        total_earnings = 0
        for shift in shifts:
            print(shift.start, shift.finish)
            earnings = calculate_shift_earnings(shift, hourly_wage_rates, 30)
            total_earnings += earnings

        return total_earnings


    # Example usage
    date = datetime(2023, 11, 9)  # Replace with the date you want to calculate the salary for
    shifts = Shift.query.filter(Shift.date == date).all()
    salary = calculate_daily_salary(date, shifts, hourly_wage_rates)
    print(f"Salary for {date}: ${salary:.2f}")
