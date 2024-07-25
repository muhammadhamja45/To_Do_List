from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from models import db, Task

tasks = Blueprint('tasks', __name__)

@tasks.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', tasks=tasks)

@tasks.route('/add', methods=['POST'])
@login_required
def add_task():
    task_name = request.form.get('task_name')
    task_date = request.form.get('task_date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    new_task = Task(user_id=current_user.id, task_name=task_name, task_date=task_date, start_time=start_time, end_time=end_time)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('tasks.index'))

@tasks.route('/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task and task.user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('tasks.index'))
