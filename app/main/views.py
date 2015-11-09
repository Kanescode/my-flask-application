# -*- coding:utf-8 -*-

from flask import render_template, redirect, url_for, request, abort, flash, current_app, make_response
from . import main
from .forms import QuestionForm, AnswerForm, CommentForm, EditForm, EditAdminForm
from flask.ext.login import current_user, login_required
from ..models import Question, Answer, Comment, User, Permission, Role, Like
from app import db
from ..permi import admin_required, permission_required

@main.route('/', methods=['GET','POST'])
def index():
    form = QuestionForm()
    if form.validate_on_submit():
        new_question = Question(title=form.title.data,
                            author=current_user._get_current_object())
        db.session.add(new_question)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_ques = False
    show_ques = bool(request.cookies.get('show_ques', ''))
    if show_ques:
        q_pagination = Question.query.order_by(Question.timestamp.desc()
                                               ).paginate(page, per_page=5, error_out=False)
        questions = q_pagination.items
        return render_template('q_index.html', form=form,
                               questions=questions, q_pagination=q_pagination, show_ques=show_ques)
    else:
        if current_user.is_authenticated and current_user.followed.count() > 10:
            a_pagination = current_user.followed_answers.order_by(
                Answer.timestamp.desc()).paginate(page, per_page=5, error_out=False)
            answers = a_pagination.items
        else:
            a_pagination = Answer.query.order_by(
                Answer.timestamp.desc()).paginate(page, per_page=5, error_out=False)
            answers = a_pagination.items
        return render_template('a_index.html', form=form,
                               answers=answers, a_pagination=a_pagination, show_ques=show_ques)

@main.route('/question/<int:id>', methods=['GET','POST'])
def question(id):
    question = Question.query.get_or_404(id)
    form = AnswerForm()
    if form.validate_on_submit():
        new_answer = Answer(body=form.body.data,
                        question_id=id,
                        author=current_user._get_current_object())
        db.session.add(new_answer)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('.question', id=id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (question.answer.count() - 1) / 5 + 1
    pagination = Answer.query.filter_by(question_id=id).paginate(page, per_page=5, error_out=False)
    answers = pagination.items
    return render_template('question.html', question=question, form=form,
                           answers=answers, pagination=pagination, id=id)

@main.route('/edit_answer/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_answer(id):
    form = AnswerForm()
    answer = Answer.query.get_or_404(id)
    if current_user == answer.author and form.validate_on_submit():
        answer.body = form.body.data
        return redirect(request.args.get('next') or url_for('.question', id=answer.question_id))
    form.body.data = answer.body
    return render_template('edit_answer.html', form=form)


@main.route('/comment/<int:id>', methods=['GET','POST'])
@login_required
def comment(id):
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(body=form.body.data,
                            answer_id=id,
                            author=current_user._get_current_object())
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('.comment', id=id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        answer = Answer.query.get_or_404(id)
        page = (answer.comment.count() - 1) / 20 + 1
    pagination = Comment.query.filter_by(answer_id=id).paginate(
        page, per_page=20, error_out=False)
    comments = pagination.items
    return render_template('comment.html', form=form,
                           comments=comments, pagination=pagination, id=id)


@main.route('/editprofile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditForm()
    if form.validate_on_submit():
        current_user.username = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        current_user.gender = form.gender.data
        db.session.add(current_user)
        flash(u'资料已经更新')
        return redirect(url_for('.profile', id=current_user.id))
    form.name.data = current_user.username
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    form.gender.data = current_user.gender
    return render_template('edit_profile.html', form=form)

@main.route('/editprofile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_admin_profile(id):
    user = User.query.get_or_404(id)
    form = EditAdminForm(user)
    if form.validate_on_submit():
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.username = form.name.data
        flash(u'资料已被修改')
        return redirect(url_for('.profile', id=user.id))
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.username
    return render_template('edit_admin_profile.html', form=form)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'非法用户')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash(u'你已经关注了该用户')
        return redirect(url_for('.profile', id=user.id))
    current_user.follow(user)
    flash(u'你已经关注了该用户')
    return redirect(url_for('.profile', id=user.id))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'非法用户')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash(u'没有关注该用户')
        return redirect(url_for('.profile', id=user.id))
    current_user.unfollow(user)
    flash (u'已经对该用户取消关注')
    return redirect(url_for('.profile', id=user.id))

@main.route('/followed/<username>')
def followed(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'非法用户')
        return redirect(url_for('.index'))
    followed_user = user.followed.all()
    return render_template('followed.html', followed_user=followed_user)

@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'非法用户')
        return redirect(url_for('.index'))
    follower = user.followers.all()
    return render_template('followers.html', follower=follower)

@main.route('/enable_answer/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENT)
def enable_answer(id):
    answer = Answer.query.get_or_404(id)
    answer.disabled = False
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('.question', id=answer.question_id))

@main.route('/disable_answer/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENT)
def disable_answer(id):
    answer = Answer.query.get_or_404(id)
    answer.disabled = True
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('.question', id=answer.question_id))

@main.route('/enable_comment/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENT)
def enable_comment(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.comment', id=comment.answer_id))

@main.route('/disable_comment/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENT)
def disable_comment(id):
    comment = Comment.query.get(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.comment', id=comment.answer_id))

@main.route('/add_like/<int:id>')
@login_required
def add_like(id):
    answer = Answer.query.get_or_404(id)
    do_you_like_me = Like.query.filter_by(answer_id=id, user_id=current_user.id).first()
    if do_you_like_me:
        return redirect(url_for('.remove_like', id=id))
    like = Like(answer=answer,
                user=current_user._get_current_object())
    db.session.add(like)
    db.session.commit()
    return redirect(url_for('.question', id=answer.question_id))

@main.route('/remove_like/<int:id>')
@login_required
def remove_like(id):
    answer = Answer.query.get_or_404(id)
    like = Like.query.filter_by(answer_id=id, user_id=current_user.id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
    return redirect(url_for('.question', id=answer.question_id))

@main.route('/who_like_you/<int:id>')
def who_like_you(id):
    answer = Answer.query.get_or_404(id)
    return render_template('who_like_you.html', answer=answer)

@main.route('/show_answer')
def show_answer():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_ques', '', max_age=30*24*60*60)
    return resp

@main.route('/show_question')
def show_question():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_ques', '1', max_age=30*24*60*60)
    return resp

'''

@main.route('/show_profile_profile/<int:id>')
def show_profile_profile(id):
    resp = make_response(redirect(url_for('.profile', id=id)))
    resp.set_cookie('show_profile_profile', '', max_age=30*24*60*60)
    # 此处设置基本资料的cookie为False时页面才会显示显示
    resp.set_cookie('show_profile_account', '', max_age=30*24*60*60)
    resp.set_cookie('show_profile_answers', '', max_age=30*24*60*60)
    resp.set_cookie('show_profile_questions', '', max_age=30*24*60*60)
    return resp
# bool('')为False,bool('0')为True

@main.route('/show_profile_account/<int:id>')
def show_profile_account(id):
    resp = make_response(redirect(url_for('.profile', id=id)))
    resp.set_cookie('show_profile_account', '1', max_age=30*24*60*60)
    resp.set_cookie('show_profile_profile', '1', max_age=30*24*60*60)
    resp.set_cookie('show_profile_answers', '', max_age=30*24*60*60)
    resp.set_cookie('show_profile_questions', '', max_age=30*24*60*60)
    return resp

@main.route('/show_profile_answers/<int:id>')
def show_profile_answers(id):
    resp = make_response(redirect(url_for('.profile', id=id)))
    resp.set_cookie('show_profile_answers', '1', max_age=30*24*60*60)
    resp.set_cookie('show_profile_account', '', max_age=30*24*60*60)
    resp.set_cookie('show_profile_profile', '1', max_age=30*24*60*60)
    resp.set_cookie('show_profile_questions', '', max_age=30*24*60*60)
    return resp

@main.route('/show_profile_questions/<int:id>')
def show_profile_questions(id):
    resp = make_response(redirect(url_for('.profile', id=id)))
    resp.set_cookie('show_profile_questions', '1', max_age=30*24*60*60)
    resp.set_cookie('show_profile_account', '', max_age=30*24*60*60)
    resp.set_cookie('show_profile_profile', '1', max_age=30*24*60*60)
    resp.set_cookie('show_profile_answers', '', max_age=30*24*60*60)
    return resp

@main.route('/profile/<int:id>', methods=['GET'])
@login_required
def profile(id):
    user = User.query.get_or_404(id)
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    show_profile_account = show_profile_profile = \
    show_profile_answers = show_profile_questions = False
    show_profile_profile = bool(request.cookies.get('show_profile_profile', ''))
    show_profile_account = bool(request.cookies.get('show_profile_account', ''))
    show_profile_answers = bool(request.cookies.get('show_profile_answers', ''))
    show_profile_questions = bool(request.cookies.get('show_profile_questions', ''))
    if not show_profile_profile:
        return render_template('profile_profile.html', user=user,
                            show_profile_profile=show_profile_profile,
                            show_profile_account=show_profile_account,
                            show_profile_answers=show_profile_answers,
                            show_profile_questions=show_profile_questions)
    if show_profile_account:
        return render_template('profile_account.html', user=user,
                            show_profile_profile=show_profile_profile,
                            show_profile_account=show_profile_account,
                            show_profile_answers=show_profile_answers,
                            show_profile_questions=show_profile_questions)
    if show_profile_answers:
        pagination = Answer.query.filter_by(author=user).paginate(page, per_page=5, error_out=False)
        return render_template('profile_answers.html',
                            page=page, pagination=pagination, user=user,
                            show_profile_profile=show_profile_profile,
                            show_profile_account=show_profile_account,
                            show_profile_answers=show_profile_answers,
                            show_profile_questions=show_profile_questions)
    if show_profile_questions:
        pagination = Question.query.filter_by(author=user).paginate(page, per_page=10, error_out=False)
        return render_template('profile_questions.html',
                            page=page, pagination=pagination, user=user,
                            show_profile_profile=show_profile_profile,
                            show_profile_account=show_profile_account,
                            show_profile_answers=show_profile_answers,
                            show_profile_questions=show_profile_questions)
    else:
        return render_template('profile_profile.html', user=user,
                            show_profile_profile=show_profile_profile,
                            show_profile_account=show_profile_account,
                            show_profile_answers=show_profile_answers,
                            show_profile_questions=show_profile_questions)

'''

@main.route('/profile/<int:id>')
@login_required
def profile(id):
    user = User.query.get_or_404(id)
    if user is None:
        abort(404)
    return render_template('profile_profile.html', user=user)

@main.route('/profile/<int:id>/account')
@login_required
def profile_account(id):
    user = User.query.get_or_404(id)
    if user is None:
        abort(404)
    if user.id != current_user.id:
        flash(u'你没有权限')
        return redirect(url_for('.index'))
    return render_template('profile_account.html', user=user)

@main.route('/profile/<int:id>/answers')
@login_required
def profile_answers(id):
    user = User.query.get_or_404(id)
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = Answer.query.filter_by(author_id=id).paginate(page, per_page=5, error_out=False)
    #answers = pagination.items
    return render_template('profile_answers.html', user=user, pagination=pagination)

@main.route('/profile/<int:id>/questions')
@login_required
def profile_questions(id):
    user = User.query.get_or_404(id)
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = Question.query.filter_by(author_id=id).paginate(page, per_page=10, error_out=False)
    #questions = pagination.items
    return render_template('profile_questions.html', user=user, pagination=pagination)