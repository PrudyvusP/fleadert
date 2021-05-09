from flask_mail import Message
from flask import current_app
from app import mail
from threading import Thread


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, recipients, html_body):
    msg = Message(current_app.config['MAIL_SUBJECT_PREFIX'] + subject, recipients=recipients)
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()


"""
Miguel comment from his blog::
In the line where you start the email sending thread, you have to pass "current_app._get_current_object()":
Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
The "current_app" object is a proxy object that looks for the application context in the current thread,
if you pass the object to another thread that does not have an application context you'll get this error.
Adding the _get_current_object() call forces the main thread to obtain the application instance, and then
pass that to the other thread.
"""
