from flask_mail import Message
from threading import Thread
from flask import current_app
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, recipients, html_body):
    msg = Message(current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, recipients=recipients)
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
