from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from .models import Shift
from . import db
from datetime import datetime, time


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        string_date = request.form.get('date')
        string_start_time = request.form.get('start_time')
        string_finish_time = request.form.get('finish_time')

        # Convert the date string to a date variable
        date = datetime.strptime(string_date, '%Y-%m-%d').date()

        # Convert the start_time and finish_time strings to time variables
        start_time = datetime.strptime(string_start_time, '%H:%M').time()
        finish_time = datetime.strptime(string_finish_time, '%H:%M').time()

        print(date, start_time, finish_time, current_user.id)
        int_start_time = int(string_start_time.replace(":", ""))
        int_finish_time = int(string_finish_time.replace(":", ""))
        if int_start_time > int_finish_time:
            int_hours = ((2400 - int_start_time) + int_finish_time) / 100
        else:
            int_hours = (int_finish_time - int_start_time) / 100
        hours = f'{int_hours}'
        data = string_date + ' ' + hours
        print(data)
        new_shift = Shift(user_id=current_user.id, date=date, start=start_time, finish=finish_time, data=data)
        db.session.add(new_shift)
        db.session.commit()
        flash('Shift added!', category='success')

    return render_template("home.html", user=current_user)

def calculate_payroll(start_date, end_date):
    shifts = Shift.query.filter(
        Shift.user_id == current_user,
        Shift.date >= start_date,
        Shift.date <= end_date
    ).all()

    base_wage = current_user.base_wage

    if shifts:
        for shift in shifts:
            shift_start = shift.start
            shift_finish = shift.finish
            shift_date = shift.date
            shift_duration = (shift_finish.hour - shift_start.hour) + (shift_finish.minute - shift_start.minute) / 60

            # if the shift is between 20:00
            if shift_start >= time(20, 0) or shift_start < time(6, 0):
                print("1")
            elif shift_date.weekday() == 4:  # Friday
                if shift_start >= time(6, 0) and shift_finish <= time(16, 0):
                    print("2")
                elif shift_start >= time(16, 0) or shift_start < time(6, 0):
                    print("3")

            if shift_duration > 9:
                print("4")

            if shift_date.weekday() == 4:
                pass

    else:
        flash('No shifts found for the given date range.', category='info')