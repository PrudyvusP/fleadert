from flask import render_template, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.email import send_email
from app.models import User
from app.auth.forms import RegisterForm, LoginForm
from app.auth import bp


@bp.route('/register/', methods=['post', 'get'])
def render_register():
    if current_user.is_authenticated:
        return redirect(url_for('main.render_index'))
    form = RegisterForm()
    if form.validate_on_submit():
        check_user_username = User.query.filter_by(username=form.username.data).first()
        check_user_email = User.query.filter_by(email=form.email.data).first()
        if check_user_email is None and check_user_username is None:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            if form.is_admin.data == 'gossopkins':
                user.is_boss = True
            db.session.add(user)
            db.session.commit()
            flash('Поздравляю, Ты зарегистрировался в сервисе! Проверь указаную тобой электронную почту!')
            send_email('Успешная регистрация', recipients=[user.email],
                       html_body=render_template('email/email_register.html', user=user))
            return redirect(url_for('auth.render_login'))
        else:
            flash('Пользователь с таким логином или почтой уже существует!')
            return redirect(url_for('auth.render_register'))
    return render_template('auth/register.html', form=form, title='Регистрация')


@bp.route('/login/', methods=["post", "get"])
def render_login():
    if current_user.is_authenticated:
        return redirect(url_for('main.render_index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('main.render_index'))
        flash('Неверное имя пользователя и (-или) пароль')
        return redirect(url_for('auth.render_login'))
    return render_template('auth/login.html', form=form, title='Войти')


@bp.route('/logout/')
@login_required
def logout():
    logout_user()
    flash("Вы успешно вышли из аккаунта")
    return redirect(url_for('auth.render_login'))

