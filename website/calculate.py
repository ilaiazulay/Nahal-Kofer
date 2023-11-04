from datetime import datetime, date, timedelta
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

    def calculate_shift_earnings_regular_day(shift, hourly_wage_rates, base_wage):
        earnings = 0
        shift_start = shift.start
        shift_finish = shift.finish
        hours = 0
        extra_hours = 0
        one_hour = timedelta(hours=1)

        while shift_start < shift_finish:
            shift_date = shift_start.date()
            if shift_start.minute == 0:
                if shift_date.weekday() in (5,) and 6 <= shift_start.hour < 16:  # Friday from 6:00 to 15:59
                    current_hour_rate = base_wage * (1.3 + extra_hours)
                elif shift_date.weekday() in (5,) and 16 <= shift_start.hour <= 23:  # friday from 16:00 to 23:59
                    current_hour_rate = base_wage * (1.5 + extra_hours)
                elif shift_date.weekday() in (6,):  # saturday all day
                    current_hour_rate = base_wage * (1.5 + extra_hours)
                elif shift_date.weekday() in (7,) and 0 <= shift_start.hour < 6:  # sunday from 00:00 to 5:59
                    current_hour_rate = base_wage * (1.5 + extra_hours)
                else:
                    current_hour_rate = base_wage * (hourly_wage_rates.get(shift_start.hour, 1.0) + extra_hours)  # Default rate is 1.0 (100%)
                    print("1", current_hour_rate)
            else:
                if shift_date.weekday() in (5,) and 6 <= shift_start.hour < 16:  # Friday from 6:00 to 15:59
                    current_hour_rate = base_wage * ((1.3 * (60 - shift_start.minute) / 60) + extra_hours)  # Default rate is 1.0 (100%)
                    print("2", current_hour_rate)
                    minutes_advance = timedelta(minutes=60 - shift_start.minute)
                    shift_start = shift_start + minutes_advance
                    current_hour_rate += base_wage * (1.3 + extra_hours)  # Default rate is 1.0 (100%)
                elif shift_date.weekday() in (5,) and 16 <= shift_start.hour <= 23:  # friday from 16:00 to 23:59
                    current_hour_rate = base_wage * ((1.5 * (60 - shift_start.minute) / 60) + extra_hours)  # Default rate is 1.0 (100%)
                    print("2", current_hour_rate)
                    minutes_advance = timedelta(minutes=60 - shift_start.minute)
                    shift_start = shift_start + minutes_advance
                    current_hour_rate += base_wage * (1.5 + extra_hours)  # Default rate is 1.0 (100%)
                elif shift_date.weekday() in (6,):  # saturday all day
                    current_hour_rate = base_wage * ((1.5 * (60 - shift_start.minute) / 60) + extra_hours)  # Default rate is 1.0 (100%)
                    print("2", current_hour_rate)
                    minutes_advance = timedelta(minutes=60 - shift_start.minute)
                    shift_start = shift_start + minutes_advance
                    current_hour_rate += base_wage * (1.5 + extra_hours)  # Default rate is 1.0 (100%)
                elif shift_date.weekday() in (7,) and 0 <= shift_start.hour < 6:  # sunday from 00:00 to 5:59
                    current_hour_rate = base_wage * ((1.5 * (60 - shift_start.minute) / 60) + extra_hours)  # Default rate is 1.0 (100%)
                    print("2", current_hour_rate)
                    minutes_advance = timedelta(minutes=60 - shift_start.minute)
                    shift_start = shift_start + minutes_advance
                    current_hour_rate += base_wage * (1.5 + extra_hours)  # Default rate is 1.0 (100%)
                else:
                    current_hour_rate = base_wage * ((hourly_wage_rates.get(shift_start.hour, 1.0) * (60 - shift_start.minute) / 60) + extra_hours)  # Default rate is 1.0 (100%)
                    print("2", current_hour_rate)
                    minutes_advance = timedelta(minutes=60 - shift_start.minute)
                    shift_start = shift_start + minutes_advance
                    current_hour_rate += base_wage * (hourly_wage_rates.get(shift_start.hour, 1.0) + extra_hours)  # Default rate is 1.0 (100%)
            if shift_start.hour == shift_finish.hour:
                if shift_start.minute != shift_finish.minute:
                    if shift_start.minute < shift_finish.minute:
                        minutes_worked = shift_finish.minute - shift_start.minute
                    else:
                        minutes_worked = 60 - shift_finish.minute + shift_start.minute
                print("earnings1 calculation", current_hour_rate * minutes_worked / 60)
                earnings += current_hour_rate * minutes_worked / 60
                print("earnings1", earnings)
                return earnings
            else:
                minutes_worked = 60
            earnings += current_hour_rate * minutes_worked / 60
            print("earnings2", earnings)

            shift_start = shift_start + one_hour
            hours += 1
            if hours >= 9:
                extra_hours = 0.25

        return earnings


    def calculate_daily_salary(start_date, finish_date, shifts, hourly_wage_rates):
        total_earnings = 0
        for shift in shifts:
            shift_date = shift.start.date()
            if start_date <= shift_date <= finish_date:
                print(shift_date, shift.start, shift.finish)
                earnings = calculate_shift_earnings_regular_day(shift, hourly_wage_rates, 30)
                total_earnings += earnings

        return total_earnings


    # Example usage
    start_date = date(2023, 11, 3)  # Replace with the date you want to calculate the salary for
    finish_date = date(2023, 11, 4)  # Replace with the date you want to calculate the salary for
    shifts = Shift.query.all()
    salary = calculate_daily_salary(start_date, finish_date, shifts, hourly_wage_rates)
    print(f"Salary for {start_date} - {finish_date}: ${salary:.2f}")
