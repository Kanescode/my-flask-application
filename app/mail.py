# -*- coding:utf-8 -*-

from threading import Thread
from flask.ext.mail import Message
from flask import current_app, render_template
from . import mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(user, body, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['MAIL_SUBJECT'],
                    sender=app.config['ZHIHUX_ADMIN'],
                    recipients=[user])
    msg.body = render_template(body + '.' + 'txt', **kwargs)
    msg.html = render_template(body + '.' + 'html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr