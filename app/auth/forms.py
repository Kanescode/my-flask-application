# -*- coding:utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms import ValidationError
from wtforms.validators import Email, Required, Length, Regexp, EqualTo
from ..models import User

class LoginForm(Form):
    email = StringField(u'电子邮件', validators=[Required(), Email(), Length(1, 32)])
    password = PasswordField(u'密码', validators=[Required(), Length(1, 32)])
    remember_me = BooleanField(u'记住我')
    submit = SubmitField(u'提交')

class RegisterForm(Form):
    email = StringField(u'电子邮件', validators=[Required(), Length(1, 64),
                                            Email()])
    username = StringField(u'用户名', validators=[Required(),
                                            Length(1, 64),
                                            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          u'用户名必须只含字母,\
                                          数字, 点或者下划线')])
    password = PasswordField(u'密码', validators=[Required(),
                                               EqualTo('password_again', message='两次输入的密码不同，请重新输入')])
    password_again = PasswordField(u'确认密码', validators = [Required()])
    submit = SubmitField(u'提交')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'电子邮件已被注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已存在')

class ResetForm(Form):
    email = StringField(u'电子邮件', validators=[Required(), Length(1, 64),
                                            Email()])
    submit = SubmitField(u'提交')

class ResetPasswordForm(Form):
    new_password = PasswordField(u'密码', validators=[Required(),
                                                     EqualTo('confirm_new_password', message='两次输入的密码不同，请重新输入')])
    confirm_new_password = PasswordField(u'确认密码', validators=[Required()])
    submit = SubmitField(u'提交')

class ChangePasswordForm(Form):
    old_password = PasswordField(u'老密码', validators=[Required()])
    new_password = PasswordField(u'新密码', validators=[Required(),
                                                             EqualTo('confirm_new_password', message='Different input password')])
    confirm_new_password = PasswordField(u'确认新密码', validators=[Required()])
    submit = SubmitField(u'提交')