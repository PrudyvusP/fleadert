import os
import imghdr
import random
import string
import json
from plotly import figure_factory as ff, io
from plotly import express as px
from plotly import graph_objects as go
from dateutil.tz import tzutc
from datetime import datetime, timezone
from sqlalchemy import func
from flask import render_template, flash, redirect, url_for, current_app, abort
from flask_login import current_user, login_required
from app import db
from app.main.forms import TaskForm, TaskExecutionForm, EditProfileForm, BossCheckRequestForm, ProjectForm
from app.models import User, Task, Request, Project, user_task_association
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
@bp.route('/index/')
@bp.route('/all_projects/')
@login_required
def render_index():
    projects = Project.query.all()
    return render_template('index.html', title="Главная", projects=projects)


@bp.route('/all_projects/<int:project_id>/')
@login_required
def render_project(project_id):
    with open("app/main/quotes.json", 'r') as f:
        data_json_list = json.load(f)
        rand_quote = random.choice(data_json_list)
    project = Project.query.get_or_404(project_id)

    tasks_at_work = Task.query.filter(Task.project_id == project_id).filter(Task.status == 'в работе') \
        .order_by(Task.deadline).all()
    tasks_on_consider = Task.query.filter(Task.project_id == project_id).filter(Task.status == 'на рассмотрении') \
        .order_by(Task.deadline).all()
    executed_tasks = Task.query.filter(Task.project_id == project_id).filter(Task.status == 'выполнена') \
        .order_by(Task.completed_on).all()
    not_completed_tasks = Task.query.filter(Task.project_id == project_id).filter(Task.status != 'выполнена') \
        .order_by(Task.deadline).all()
    count_executed_tasks = db.session.query(User.username, func.count(User.username).label('count')) \
        .join(Task, Task.executor_id == User.id).filter(Task.project_id == project_id).group_by(User.username).all()
    if project.tasks:
        pie_labels = []
        pie_values = []
        gannt_list = []
        for task in count_executed_tasks:
            pie_labels.append(task.username)
            pie_values.append(task.count)

        pie_fig = go.Figure(data=[go.Pie(labels=pie_labels, values=pie_values, hole=.3)])
        pie_fig.update_layout(title_text="Распределение выполненных задач проекта по исполнителям", )
        pie_fig = io.to_html(pie_fig, include_plotlyjs=False, full_html=False)

        if not_completed_tasks:
            for task in not_completed_tasks:
                for user in task.users:
                    gannt_list.append(dict(Task=task.name, Start=utc_dt_to_local_dt(task.created_on),
                                           Finish=utc_dt_to_local_dt(task.deadline),
                                           Исполнитель=user.username))
            fig = ff.create_gantt(gannt_list, index_col='Исполнитель',
                                  title='Диаграмма Ганта для проекта {}'.format(project.name),
                                  show_colorbar=True, showgrid_y=True, group_tasks=True)
            fig.update_layout(title_font_size=24, template='plotly_white')
            if len(gannt_list) > 3:
                fig.update_yaxes(autorange='reversed')
            fig = io.to_html(fig, include_plotlyjs=False, full_html=False)
            return render_template('project.html', title="Проект", project=project, quote=rand_quote.get("quote"),
                                   author=rand_quote.get("author"), fig=fig, work=tasks_at_work,
                                   consider=tasks_on_consider, executed=executed_tasks, pie=pie_fig)
        return render_template('project.html', title="Проект", project=project, quote=rand_quote.get("quote"),
                               author=rand_quote.get("author"), work=tasks_at_work,
                               consider=tasks_on_consider, executed=executed_tasks, pie=pie_fig)
    return render_template('project.html', title="Проект", project=project, quote=rand_quote.get("quote"),
                           author=rand_quote.get("author"))


@bp.route('/my_tasks/<username>/')
@login_required
def render_tasks_list(username):
    query_user = User.query.filter_by(username=username).first_or_404()
    tasks_query = Task.query.join(user_task_association, (user_task_association.c.task_id == Task.id)).join(User, (
            user_task_association.c.user_id == User.id)).filter(Task.status != 'выполнена').order_by(Task.deadline)
    tasks_for_boss = tasks_query.all()
    tasks_for_user = tasks_query.filter(User.username == username).all()
    if tasks_for_boss:
        gannt_list = []
        timeline_list = []
        for task in tasks_for_boss:
            for user in task.users:
                gannt_list.append(dict(Task=task.name,
                                       Start=utc_dt_to_local_dt(task.created_on),
                                       Finish=utc_dt_to_local_dt(task.deadline),
                                       Исполнитель=user.username))
                timeline_list.append(dict(Задача=task.name, Начало=task.created_on, Завершение=task.deadline,
                                          Исполнитель=user.username))

        gannt = ff.create_gantt(gannt_list, index_col='Исполнитель', title='Диаграмма Ганта для актуальных задач',
                                show_colorbar=True, showgrid_y=True, group_tasks=True)
        if len(gannt_list) > 3:
            gannt.update_yaxes(autorange='reversed')
        gannt.update_layout(title_font_size=24, template='plotly_white')
        gannt = io.to_html(gannt, include_plotlyjs=False, full_html=False)

        timeline = px.timeline(timeline_list, x_start="Начало", x_end="Завершение", color='Исполнитель', opacity=0.7,
                               y="Задача", template='plotly_white', title='Диаграмма Ганта для проекта')
        timeline = io.to_html(timeline, include_plotlyjs=False, full_html=False)

        return render_template('my_tasks.html', title="Задачи", gannt_fig=gannt, timeline_fig=timeline,
                               tasks_for_user=tasks_for_user, tasks_for_boss=tasks_for_boss, user=query_user)
    return render_template('my_tasks.html', user=query_user, tasks_for_user=tasks_for_user,
                           tasks_for_boss=tasks_for_boss, title="Задачи")


@bp.route('/user/<username>/', methods=['get'])
@login_required
def render_user_page(username):
    query_user = User.query.filter_by(username=username).first_or_404()

    test = Task.query.join(user_task_association, (user_task_association.c.task_id == Task.id)).join(User, (
                user_task_association.c.user_id == User.id)).filter(User.username == username).all()

    return render_template('user.html', user=query_user, title="Личный кабинет")


@bp.route('/edit_profile/<int:user_id>/', methods=['post', 'get'])
@login_required
def render_edit_profile(user_id):
    user = User.query.get_or_404(user_id)
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
        return redirect(url_for('main.render_user_page', username=current_user.username))
    form.name.data = user.name
    form.email.data = user.email
    form.phone.data = user.phone
    return render_template('user_edit.html', form=form, title='Изменить данные')


@bp.route('/create_project/', methods=['post', 'get'])
@login_required
def render_create_project():
    if current_user.is_boss is True:
        form = ProjectForm()
        if form.validate_on_submit():
            new_project = Project(name=form.name.data, description=form.description.data, author=current_user.username)
            db.session.add(new_project)
            db.session.commit()
            flash('Проект {} успешно создан'.format(new_project.name))
            return redirect(url_for('main.render_create_task'))
        return render_template('create_project.html', form=form, title='Создать проект')
    return abort(403)


@bp.route('/create_task/', methods=['post', 'get'])
@login_required
def render_create_task():
    if current_user.is_boss is True:
        executors = User.query.filter(User.is_boss.is_(False)).order_by(User.username).all()
        projects = Project.query.all()
        form = TaskForm()
        form.users.choices = [(exe.id, exe.username) for exe in
                              User.query.filter(User.is_boss.is_(False)).order_by(User.username).all()]
        form.project.choices = [(project.id, project.name) for project in Project.query.all()]
        if form.validate_on_submit():
            executors_list = []
            executors_emails_list = []
            for executor_id in form.users.data:
                executor = User.query.get_or_404(executor_id)
                executors_list.append(executor)
                executors_emails_list.append(executor.email)
            new_task = Task(name=form.name.data, description=form.description.data,
                            deadline=form.deadline.data.astimezone(tzutc()), author=current_user.username,
                            users=executors_list, priority=form.priority.data,
                            project=Project.query.get_or_404(int(form.project.data)))
            db.session.add(new_task)
            db.session.commit()
            send_email('Новая задача', recipients=executors_emails_list,
                       html_body=render_template('email/email_task_created.html', task=new_task))
            return redirect(url_for('main.render_task_created', task_id=new_task.id))
        return render_template('create_task.html', form=form, users=executors, projects=projects, title="Создать задачу")
    return abort(403)


@bp.route('/task_created/<int:task_id>/')
@login_required
def render_task_created(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template('task_created.html', task=task, title="Успешное создание задачи")


@bp.route('/send_task_execution/<username>/<int:task_id>/', methods=['get', 'post'])
@login_required
def render_task_execution(username, task_id):
    task = Task.query.get_or_404(task_id)
    if task.status == "на рассмотрении":
        abort(404)
    user = User.query.filter_by(username=username).first_or_404()
    bosses = User.query.filter(User.is_boss.is_(True)).all()
    bosses_email_list = []
    for boss in bosses:
        bosses_email_list.append(boss.email)
    form = TaskExecutionForm()
    if form.validate_on_submit():
        print(form.date_of_execution.data, type(form.date_of_execution.data))
        new_request = Request(user=user, task=task, executed_comment=form.comment.data,
                              executed_number=form.number_of_execution.data)
        if form.date_of_execution.data is not None:
            date_of_execution = form.date_of_execution.data
            date_of_execution = datetime(date_of_execution.year, date_of_execution.month, date_of_execution.day)
            new_request.date_of_execution = date_of_execution
        db.session.add(new_request)
        task.status = 'на рассмотрении'
        db.session.commit()
        flash('Ваша заявка выполнения задачи успешно передана руководству на рассмотрение!')
        send_email('Новый запрос', recipients=bosses_email_list,
                   html_body=render_template('email/email_send_task.html', request=new_request))
        return redirect(url_for('main.render_tasks_list', username=username))
    return render_template('send_task.html', form=form, task=task, title="Отправить исполнение задачи")


@bp.route('/confirm_task_execution/<int:task_id>/', methods=['get', 'post'])
@login_required
def render_task_confirmation(task_id):
    task = Task.query.get_or_404(task_id)
    task_request = Request.query.filter_by(task=task).filter(Request.is_considered.is_(False)).first_or_404()
    if current_user.is_boss is True:
        form = BossCheckRequestForm()
        if form.validate_on_submit():
            if form.submit.data is True:
                task.status = "выполнена"
                task.completed_on = datetime.utcnow()
                task.executed_number = task_request.executed_number
                task.executed_date = task_request.date_of_execution
                task.executor = task_request.user
                task.closer = current_user
            if form.reject.data is True:
                task.status = "в работе"
                task_request.denied_on = datetime.utcnow()
            task_request.considered_on = datetime.utcnow()
            task_request.is_considered = True
            task_request.boss_comment = form.comment.data
            db.session.commit()
            return redirect(url_for('main.render_tasks_list', username=current_user.username))
        return render_template('task_checked.html', form=form, title="Рассмотрение заявки", task=task,
                               task_request=task_request)
    return abort(403)


@bp.route('/all_users/')
@login_required
def render_all_users():
    users = User.query.order_by(User.is_boss.desc()).all()
    return render_template('all_users.html', title="Все пользователи", users=users)


@bp.route('/admin/')
@login_required
def render_admin():
    return render_template('test.html', title="Админка")


# TODO поиск
# TODO приложение файла к заявке
# TODO изменение записей
