from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Regexp, EqualTo, ValidationError
from app.models import db, User


class RegisterForm(FlaskForm):
    username = StringField('Логин', validators=[InputRequired(message="Заполните поле")])
    email = StringField('E-mail', validators=[InputRequired(), Regexp('^[-\w.]+@([A-z0-9][-A-z0-9]+\.)+[A-z]{2,5}$',
                                                                      message="Введите корректный e-mail")])
    password = PasswordField('Пароль', validators=[InputRequired()])
    password2 = PasswordField('Повторите пароль', validators=[InputRequired(),
                                                              EqualTo('password', message='Пароли должны совпадать')])
    is_admin = StringField('Введите кодовое слово для получения прав начальника')
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = db.session.query(User).filter(User.username == username.data).first()
        if user: raise ValidationError('Пользователь с таким именем уже существует. Пожалуйста, выберете другой ник.')

    def validate_email(self, email):
        user = db.session.query(User).filter(User.email == email.data).first()
        if user: raise ValidationError('Пользователь с такой почтой уже существует. Пожалуйста, выберете другую почту')


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[InputRequired(message="Заполните поле")])
    password = PasswordField('Пароль', validators=[InputRequired(message="Заполните поле")])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

