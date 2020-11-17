from flask_wtf import FlaskForm
from datetime import datetime, timedelta
from flask_wtf.file import FileField
from wtforms import TextAreaField, StringField, SubmitField, RadioField, DateTimeField,\
    SelectMultipleField, SelectField
from wtforms.validators import InputRequired, Regexp, ValidationError
from app.models import User


class TaskForm(FlaskForm):
    name = StringField('Название задачи', validators=[InputRequired(message="Заполните поле")])
    description = TextAreaField('Описание задачи', validators=[InputRequired(message="Заполните поле")])
    deadline = DateTimeField('Срок:', default=datetime.now()+timedelta(days=1), format='%Y-%m-%d %H:%M')
    users = SelectMultipleField('Исполнители', choices=[], coerce=int, validators=[InputRequired(message="Заполните "
                                                                                                         "поле")])
    priority = RadioField('Приоритет:', choices=[("высокий", "высокий"), ("средний", "средний"), ("низкий", "низкий")],
                          default="средний")
    project = SelectField('Проект', choices=[], coerce=int, validators=[InputRequired(message="Заполните поле")])
    submit = SubmitField('Создать')

    def validate_deadline(self, field):
        if type(field.data) is not datetime:
            raise ValidationError(message="Проверьте правильность написания даты")
        elif field.data < datetime.today():
            raise ValidationError(message="Дедлайн вчерашним числом - залог успешной работы, но не здесь")


class ProjectForm(FlaskForm):
    name = StringField('Название проекта', validators=[InputRequired(message="Заполните поле")])
    description = TextAreaField('Описание проекта', validators=[InputRequired(message="Заполните поле")])
    submit = SubmitField('Создать')


class TaskExecutionForm(FlaskForm):
    comment = TextAreaField('Комментарий', validators=[InputRequired(message='Заполните поле')])
    number_of_execution = StringField('Номер исполнения (при наличии):')
    submit = SubmitField('Отправить')


class BossCheckRequestForm(FlaskForm):
    comment = TextAreaField('Комментарий руководства', default='Спасибо за работу! Родина не забудет!',
                            validators=[InputRequired(message='Заполните поле')])
    submit = SubmitField(label='Принять')
    reject = SubmitField(label='На доработку')


class EditProfileForm(FlaskForm):
    file = FileField('Аватар')
    name = StringField('Ваше имя')
    email = StringField('E-mail', validators=[InputRequired(), Regexp('^[-\w.]+@([A-z0-9][-A-z0-9]+\.)+[A-z]{2,5}$',
                                                                      message="Введите корректный e-mail")])
    phone = StringField('Номер телефона')
    submit = SubmitField('Сохранить изменения')

    def __init__(self, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        if email.data != self.original_email:
            email = User.query.filter_by(email=self.email.data).first()
            if email is not None:
                raise ValidationError('Пожалуйста, выберите другую почту')
