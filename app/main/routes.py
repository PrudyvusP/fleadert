import os
import imghdr
import random
import string
import json
from plotly import figure_factory as ff, io
from plotly import graph_objects as go
from dateutil.tz import tzutc
from datetime import datetime, timezone
from sqlalchemy import func
from flask import render_template, flash, redirect, url_for, current_app, abort, request
from flask_login import current_user, login_required
from app import db
from app.main.forms import TaskForm, TaskExecutionForm, EditProfileForm, BossCheckRequestForm, ProjectForm
from app.models import User, Task, Request, Project
from app.main import bp
from app.email import send_email


def utc_dt_to_local_dt(utc_dt):
    local_dt = utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
    return local_dt


def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')


def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        db.session.commit()


@bp.route('/')
@bp.route('/index')
def render_index():
    return "main"


@bp.route('/projects')
@login_required
def render_projects():
    projects = Project.query.all()
    return render_template('projects.html', title="Главная", projects=projects)


@bp.route('/projects/<int:project_id>', methods=['GET'])
@login_required
def render_project(project_id):
    with open("app/main/quotes.json", 'r') as f:
        data_json_list = json.load(f)
        rand_quote = random.choice(data_json_list)
    project = Project.query.get_or_404(project_id)
    count_tasks_into_project = len(project.tasks)
    tasks_at_work, tasks_on_consider = project.tasks_at_work, project.tasks_on_consider
    tasks_executed = project.tasks_executed
    tasks_not_executed = []
    tasks_not_executed.extend(tasks_at_work)
    tasks_not_executed.extend(tasks_on_consider)
    if project.tasks:
        user_tasks_query = db.session.query(User.username, func.count(User.username).label('count_executed_tasks')) \
            .join(Task, Task.executor_id == User.id).filter(Task.project_id == project_id).group_by(User.username).all()
        pie_labels = [task.username for task in user_tasks_query]
        pie_values = [task.count_executed_tasks for task in user_tasks_query]
        pie_fig = go.Figure(data=[go.Pie(labels=pie_labels, values=pie_values, hole=.3)])
        pie_fig.update_layout(title_text="Распределение выполненных задач проекта по исполнителям", )
        pie_fig = io.to_html(pie_fig, include_plotlyjs=False, full_html=False)

        gannt_list = [dict(Task=task.name, Start=utc_dt_to_local_dt(task.created_on),
                           Finish=utc_dt_to_local_dt(task.deadline),
                           Исполнитель=user.username) for task in tasks_not_executed for user in task.users if
                      tasks_not_executed]
        if gannt_list:
            fig = ff.create_gantt(gannt_list, index_col='Исполнитель',
                                  title=f'Диаграмма Ганта для проекта {project.name}.', show_colorbar=True,
                                  showgrid_y=True, group_tasks=True)
            fig.update_layout(title_font_size=24, template='plotly_white')
            if len(gannt_list) > 3: fig.update_yaxes(autorange='reversed')
            fig = io.to_html(fig, include_plotlyjs=False, full_html=False)
            return render_template('project.html', title="Проект", project=project, quote=rand_quote.get("quote"),
                                   author=rand_quote.get("author"), fig=fig, work=tasks_at_work,
                                   consider=tasks_on_consider, count_tasks_into_project=count_tasks_into_project,
                                   executed=tasks_executed, pie=pie_fig)
        return render_template('project.html', title="Проект", project=project, quote=rand_quote.get("quote"),
                               author=rand_quote.get("author"), work=tasks_at_work,
                               consider=tasks_on_consider, executed=tasks_executed,
                               count_tasks_into_project=count_tasks_into_project, pie=pie_fig)
    return render_template('project.html', title="Проект", project=project, quote=rand_quote.get("quote"),
                           author=rand_quote.get("author"), count_tasks_into_project=count_tasks_into_project)


@bp.route('/create_project', methods=['GET', 'POST'])
@login_required
def render_create_project():
    if current_user.is_boss is True:
        form = ProjectForm()
        if form.validate_on_submit():
            new_project = Project(name=form.name.data, description=form.description.data, author=current_user.username)
            db.session.add(new_project)
            db.session.commit()
            flash(f'Проект {new_project.name} успешно создан')
            return redirect(url_for('main.render_project', project_id=new_project.id))
        return render_template('create_project.html', title='Создать проект', form=form)
    return abort(403)


@bp.route('/tasks', methods=['GET'])
@login_required
def render_tasks():
    page = request.args.get('page', 1, type=int)
    tasks = db.session.query(Task) \
        .order_by(Task.status, Task.deadline) \
        .paginate(page, current_app.config['TASKS_PER_PAGE'], False)
    next_url = url_for('main.render_tasks', page=tasks.next_num) \
        if tasks.has_next else None
    prev_url = url_for('main.render_tasks', page=tasks.prev_num) \
        if tasks.has_prev else None
    return render_template('tasks.html', title='Задачи', tasks=tasks.items, next_url=next_url, prev_url=prev_url)


@bp.route('/create_task', methods=['GET', 'POST'])
@login_required
def render_create_task():
    if current_user.is_boss:
        form = TaskForm()
        executors = db.session.query(User).filter(User.is_boss.is_(False)).order_by(User.username).all()
        projects = db.session.query(Project).filter(Project.is_relevant.is_(True)).all()
        form.users.choices = [(executor.id, executor.username) for executor in executors]
        form.project.choices = [(project.id, project.name) for project in projects]
        if form.validate_on_submit():
            executors_lst = [db.session.query(User).get_or_404(executor_id) for executor_id in form.users.data]
            executors_emails_lst = [executor.email for executor in executors_lst]
            deadline = form.deadline_date.data.strftime("%Y-%m-%d") + ' ' + form.deadline_time.data.strftime("%H:%M:%S")
            deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
            new_task = Task(name=form.name.data, description=form.description.data,
                            deadline=deadline.astimezone(tzutc()), author=current_user, users=executors_lst,
                            priority=form.priority.data,
                            project=db.session.query(Project).get_or_404(form.project.data))
            db.session.add(new_task)
            db.session.commit()
            # send_email('Новая задача', recipients=executors_emails_lst,
            #           html_body=render_template('email/email_task_created.html', task=new_task))
            return redirect(url_for('main.render_task_created', task_id=new_task.id))
        return render_template('create_task.html', title="Создать задачу", form=form)
    return abort(403)


@bp.route('/task_created/<int:task_id>', methods=['GET'])
@login_required
def render_task_created(task_id):
    task = db.session.query(Task).get_or_404(task_id)
    return render_template('task_created.html', title="Успешное создание задачи", task=task)


@bp.route('/tasks/<int:task_id>/execute', methods=['GET', 'POST'])
@login_required
def render_task_execution(task_id):
    task = Task.query.get_or_404(task_id)
    if (task.status != 'в работе' and not current_user.is_boss)\
            or current_user.id not in [user.id for user in task.users]:
        abort(403)
    bosses_email_list = [boss.email for boss in db.session.query(User).filter(User.is_boss.is_(True)).all()]
    form = TaskExecutionForm()
    if form.validate_on_submit():
        date_of_execution = form.executed_date.data
        if date_of_execution:
            new_request = Request(user=current_user, task=task, executed_comment=form.comment.data,
                                  executed_number=form.executed_number.data, date_of_execution=date_of_execution)
        else:
            new_request = Request(user=current_user, task=task, executed_comment=form.comment.data,
                                  executed_number=form.executed_number.data)
        db.session.add(new_request)
        task.status = 'на рассмотрении'
        db.session.commit()
        flash('Ваша заявка выполнения задачи успешно передана руководству на рассмотрение!')
        # send_email('Новый запрос', recipients=bosses_email_list,
        #           html_body=render_template('email/email_send_task.html', request=new_request))
        return redirect(url_for('main.render_tasks'))
    return render_template('execute_task.html', title="Отправить исполнение задачи", form=form, task=task)


@bp.route('/tasks/<int:task_id>/confirm', methods=['GET', 'POST'])
@login_required
def render_task_confirmation(task_id):
    task = db.session.query(Task).get_or_404(task_id)
    task_request_query = db.session.query(Request).filter(Request.task == task)\
        .filter(Request.is_considered.is_(False)).first_or_404()
    if current_user.is_boss:
        form = BossCheckRequestForm()
        if form.validate_on_submit():
            if form.submit.data:
                task.status = "выполнена"
                task.completed_on = datetime.utcnow()
                task.executed_number = task_request_query.executed_number
                task.executed_date = task_request_query.date_of_execution
                task.executor = task_request_query.user
                task.closer = current_user.username
                flash('Заявка на исполнение успешно принята')
            if form.reject.data:
                task.status = "в работе"
                task_request_query.denied_on = datetime.utcnow()
                flash('Задача на исполнение отклонена')
            task_request_query.considered_on = datetime.utcnow()
            task_request_query.is_considered = True
            task_request_query.boss_comment = form.comment.data
            db.session.commit()
            return redirect(url_for('main.render_tasks'))
        return render_template('check_task.html', title="Рассмотрение заявки", form=form, task=task,
                               task_request=task_request_query)
    return abort(403)


@bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def render_edit_profile(user_id):
    if current_user.id != user_id:
        abort(403)
    user = db.session.query(User).get_or_404(user_id)
    form = EditProfileForm(current_user.email)
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.phone = form.phone.data
        if form.file.data is not None:
            uploaded_file = form.file.data
            filename = uploaded_file.filename
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in current_app.config['ALLOWED_EXTENSIONS'] or file_ext != validate_image(
                        uploaded_file.stream):
                    return abort(400)
                if user.avatar != 'default.png':
                    os.remove(os.path.join(current_app.config['UPLOADED_FILES_DEST'], user.avatar))
                avatar_name = get_random_alphanumeric_string(10)
                uploaded_file.save(os.path.join(current_app.config['UPLOADED_FILES_DEST'], avatar_name))
                user.avatar = avatar_name
        db.session.commit()
        flash('Данные успешно обновлены')
        return redirect(url_for('main.render_user', user_id=current_user.id))
    form.name.data = user.name
    form.email.data = user.email
    form.phone.data = user.phone
    return render_template('edit_user.html', form=form, title='Изменить данные')


@bp.route('/users', methods=['GET'])
@login_required
def render_users():
    users = db.session.query(User).order_by(User.is_boss.desc(), User.username).all()
    return render_template('users.html', title="Пользователи", users=users)


@bp.route('/user/<int:user_id>', methods=['GET'])
@login_required
def render_user(user_id):
    user = db.session.query(User).get_or_404(user_id)
    non_executed_tasks = user.non_executed_tasks
    authorship_tasks = db.session.query(Task).join(User, Task.users).filter(Task.author == user).all()
    return render_template('user.html', title="Личный кабинет", user=user, non_executed_tasks=non_executed_tasks,
                           authorship_tasks=authorship_tasks)


@bp.route('/admin/')
@login_required
def render_admin():
    return render_template('test.html', title="Админка")
