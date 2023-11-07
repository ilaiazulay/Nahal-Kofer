from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Shift
from . import db
from datetime import datetime, time
import json


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        string_start_time = request.form.get('start_time')
        string_finish_time = request.form.get('finish_time')

        string_start_time = (string_start_time.replace("T", " "))
        string_finish_time = (string_finish_time.replace("T", " "))

        print(string_start_time, string_finish_time)

        # Convert the start_time and finish_time strings to time variables
        start_time = datetime.strptime(string_start_time, '%Y-%m-%d %H:%M')
        finish_time = datetime.strptime(string_finish_time, '%Y-%m-%d %H:%M')
        print(start_time, finish_time, current_user.id)
        # Calculate the duration between start_time and finish_time
        duration = finish_time - start_time
        print(duration)

        # Extract the total hours from the duration
        float_hours = duration.total_seconds() / 3600  # 3600 seconds in an hour
        hours = f'{float_hours}'

        if float_hours > 48:
            flash('Shifts can not be longer then 48 hours', category='error')

        elif start_time > finish_time:
            flash('Start of the shift can not be after the end of the shift', category='error')

        else:
            data = string_start_time + ' ' + string_finish_time + ' ' + hours
            print(data)
            new_shift = Shift(user_id=current_user.id, start=start_time, finish=finish_time, data=data)
            db.session.add(new_shift)
            db.session.commit()
            flash('Shift added!', category='success')
            return redirect(url_for('views.home'))

    return render_template("home.html", user=current_user)


@views.route('/delete-shift', methods=['POST'])
def delete_shift():
    shift = json.loads(request.data)
    shift_id = shift['shiftId']
    shift = Shift.query.get(shift_id)
    if shift:
        if shift.user_id == current_user.id:
            db.session.delete(shift)
            db.session.commit()

    return jsonify({})
