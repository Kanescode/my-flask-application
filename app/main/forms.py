# -*- coding:utf-8 -*-

from flask.ext.wtf import Form
from flask.ext.pagedown.fields import PageDownField
from wtforms.validators import Required
from wtforms import SubmitField, StringField, SelectField, TextAreaField, BooleanField
from ..models import Role

class QuestionForm(Form):
    title = StringField(u"你想问些什么？", validators=[Required()])
    submit = SubmitField(u"提交")

class AnswerForm(Form):
    body = PageDownField(validators=[Required()])
    submit = SubmitField(u'提交')

class CommentForm(Form):
    body = PageDownField(validators=[Required()])
    submit = SubmitField(u'提交')

class EditForm(Form):
    name = StringField(u'用户名')
    gender = SelectField(u'性别', choices=[(1, u'男'), (2, u'女')], coerce=int)
    location = StringField(u'位置')
    about_me = TextAreaField(u'自我描述')
    submit = SubmitField(u'提交')

class EditAdminForm(Form):
    confirmed = BooleanField(u'确认账户')
    role = SelectField(u'角色', coerce=int)
    name = StringField(u'用户名')
    gender = SelectField(u'性别', choices=[(1, u'男'), (2, u'女')], coerce=int)
    location = StringField(u'位置')
    about_me = TextAreaField(u'自我描述')
    submit = SubmitField(u'提交')

    def __init__(self, user, *args, **kwargs):
        super(EditAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)for role in Role.query.order_by(Role.name).all()]
        self.user = user