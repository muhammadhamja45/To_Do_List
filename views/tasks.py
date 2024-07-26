from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Task

tasks = Blueprint('tasks', __name__)

@tasks.route('/')
@login_required
def index():
    user_tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', tasks=user_tasks)

@tasks.route('/add', methods=['POST'])
@login_required
def add_task():
    task_name = request.form.get('task_name')
    task_date = request.form.get('task_date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    status = request.form.get('status')
    new_task = Task(user_id=current_user.id, task_name=task_name, task_date=task_date, start_time=start_time, end_time=end_time, status=status)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('tasks.index'))

@tasks.route('/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if task and task.user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('tasks.index'))

@tasks.route('/update', methods=['POST'])
@login_required
def update_tasks():
    user_tasks = Task.query.filter_by(user_id=current_user.id).all()
    for task in user_tasks:
        task.task_name = request.form.get(f'task_name_{task.id}')
        task.task_date = request.form.get(f'task_date_{task.id}')
        task.start_time = request.form.get(f'start_time_{task.id}')
        task.end_time = request.form.get(f'end_time_{task.id}')
        task.status = request.form.get(f'status_{task.id}')
    db.session.commit()
    return redirect(url_for('tasks.index'))
