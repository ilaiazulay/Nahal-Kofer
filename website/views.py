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

        # Extract the total hours from the duration
        float_hours = duration.total_seconds() / 3600  # 3600 seconds in an hour
        hours = f'{float_hours}'
        data = string_start_time + ' ' + string_finish_time + ' ' + hours
        print(data)
        new_shift = Shift(user_id=current_user.id, start=start_time, finish=finish_time, data=data)
        db.session.add(new_shift)
        db.session.commit()
        flash('Shift added!', category='success')

    return render_template("home.html", user=current_user)
