from flask_wtf import FlaskForm
from datetime import datetime, timedelta, time, date
from flask_wtf.file import FileField
from wtforms import TextAreaField, StringField, SubmitField, RadioField, SelectMultipleField, SelectField
from wtforms.validators import InputRequired, Regexp, ValidationError, Optional
from wtforms.fields.html5 import DateField, TimeField
from app.models import User


class TaskForm(FlaskForm):
    name = StringField('Название задачи', validators=[InputRequired(message="Заполните поле")])
    description = TextAreaField('Описание задачи', validators=[InputRequired(message="Заполните поле")])
    deadline_date = DateField('Срок:', default=datetime.now().date()+timedelta(days=1),
                              validators=[InputRequired(message='Заполните поле')])
    deadline_time = TimeField('', default=time(hour=9, minute=0), validators=[InputRequired()])
    users = SelectMultipleField('Исполнитель(-ли)', choices=[], coerce=int,
                                validators=[InputRequired(message="Заполните поле")])
    priority = RadioField('Приоритет:', choices=[("высокий", "высокий"), ("средний", "средний"), ("низкий", "низкий")],
                          default="средний")
    project = SelectField('Выберете проект', choices=[], coerce=int,
                          validators=[InputRequired(message="Заполните поле")])
    submit = SubmitField('Создать')


    def validate_deadline_time(self, field):
        if not isinstance(field.data, time):
            raise ValidationError(message="Проверьте правильность написания времени")
        elif field.data < datetime.now().time() and self.deadline_date.data <= date.today():
            raise ValidationError(message="Проверьте время")
        elif self.deadline_date.data <= date.today():
            raise ValidationError(message="Проверьте дату")


class ProjectForm(FlaskForm):
    name = StringField('Название проекта', validators=[InputRequired(message="Заполните поле")])
    description = TextAreaField('Описание проекта', validators=[InputRequired(message="Заполните поле")])
    submit = SubmitField('Создать')


class TaskExecutionForm(FlaskForm):
    comment = TextAreaField('Комментарий', validators=[InputRequired(message='Заполните поле')])
    executed_number = StringField('Номер исполнения (при наличии):')
    executed_date = DateField('Дата исполнения (в случае письма/протокола и т.д.):', validators=[Optional()])
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
