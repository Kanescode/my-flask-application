# -*- coding:utf-8 -*-

from flask import redirect, render_template, flash, url_for, request, current_app
from flask.ext.login import current_user, login_required, login_user, logout_user
from ..models import User
from .. import db
from . import auth
from .forms import LoginForm, RegisterForm, ResetForm, ResetPasswordForm, ChangePasswordForm
from ..mail import send_email
from werkzeug.security import generate_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed', methods=['GET'])
@login_required
def unconfirmed():
    if current_user.confirmed or current_user.is_anonymous:
        return redirect('main.index')
    return render_template('unconfirmed.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            flash(u'欢迎')
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'账号或密码错误')
    return render_template('auth/login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email,
                  'auth/email/confirm', token=token)
        flash(u'邮件已发送至你的邮箱，请检查')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('Your account has been confirmed')
    else:
        flash(u'认证失败，请重新认证')
    return redirect(url_for('main.index'))

@auth.route('/reset', methods=['GET', 'POST'])
def reset():
    form = ResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            token = user.generate_confirmation_token()
            send_email(user.email,
                      'auth/email/reset_password',
                       token=token, userid=user.id)
            flash('An email has been sent to your mailbox')
            return redirect(url_for('auth.login'))
        flash('User isn\'t exist')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset.html', form=form)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm()
    s = Serializer(current_app.config['SECRET_KEY'])
    id = (s.loads(token)).get('confirm')
    user = User.query.get_or_404(id)
    if form.validate_on_submit():
        if user.confirm(token):
            user.password_hash = generate_password_hash(form.new_password.data)
            db.session.add(user)
            db.session.commit()
            flash(u'账户密码已被修改')
            return redirect(url_for('auth.login'))
        else:
            flash(u'非法令牌，请重新验证')
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/change_password', methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit() and \
        current_user.verify_password(form.old_password.data):
        current_user.password_hash = \
            generate_password_hash(form.new_password.data)
        db.session.add(current_user)
        db.session.commit()
        logout_user()
        flash(u'你的密码已被修改，请重新登录')
        return redirect(url_for('auth.login'))
    return render_template('auth/change_password.html', form=form)

@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/resend_email', methods=['GET'])
@login_required
def resend():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email,
               'auth/email/confirm', token=token)
    flash(u'邮件已经发送，请查收')
    return redirect(url_for('main.index'))