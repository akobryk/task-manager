import os
from datetime import datetime
from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import app, db
from .models import User
from .forms import (
    RegisterForm, LoginForm, ResetPasswordForm, UserResetPasswordForm, UpdateProfileForm
    )
from .utils import send_email, generate_confirmation_token, confirm_token
from .decorators import check_confirmed


@app.route('/')
@login_required
@check_confirmed
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        check_username = User.query.filter_by(username=form.username.data).first()
        check_email = User.query.filter_by(email=form.username.data).first()
        if not check_username and not check_email:
            user = User(
                username=form.username.data,
                full_name=form.full_name.data,
                password=form.password.data,
                email=form.email.data
                )
            db.session.add(user)
            db.session.commit()

            token = generate_confirmation_token(user.email)
            confirm_url = url_for('confirm_email', token=token, _external=True)
            html = render_template('users/activate_account.html', confirm_url=confirm_url)
            subject = 'Please confirm your account'

            send_email(user.email, subject, html)
            login_user(user)
            flash('A confirmation email has been sent via email.', 'info')

            return redirect(url_for('index'))

        else:
            if check_username:
                form.username.errors.append('A user with with this username already exists.')
            if check_email:
                form.email.errors.append('A user with this email already exists.')

    return render_template('users/register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
            user = \
                User.query.filter_by(username=form.username.data).first() or \
                User.query.filter_by(email=form.username.data).first()
            if user and user.is_correct_password(form.password.data):
                login_user(user)
                user.last_login = db.func.now()
                db.session.commit()
                flash('Logged in successfully.', 'info')
                return redirect(url_for('index'))
            else:
                if not user:
                    form.username.errors.append('Invaild username/email.')
                else:
                    form.password.errors.append('Invalid password.')
    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)

    except Exception:
        flash('The confimation link is invalid or has expired.', 'error')

    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed and current_user.is_anonymous:
        flash('Account already confirmed. Please login.', 'info')
    elif user.confirmed and current_user.is_authenticated:
        flash('Account already confirmed.', 'info')

    else:
        user.confirmed = True
        user.confirmed_on = datetime.now()
        db.session.commit()
        flash('You have confirmed your account.', 'info')

    return redirect(url_for('index'))


@app.route('/resend-confirmation')
@login_required
def resend_confirmation():
    token = generate_confirmation_token(current_user.email)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    html = render_template('activate_account.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(current_user.email, subject, html)
    flash('A new confirmation email has been sent.', 'info')
    return redirect(url_for('index'))


@app.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect('index')
    return render_template('users/unconfirmed.html')


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    form = UserResetPasswordForm()
    if form.validate_on_submit():
        user = \
            User.query.filter_by(username=form.username.data).first() or \
            User.query.filter_by(email=form.username.data).first()

        if not user:
            form.username.errors.append('There is no user with the specified username or password.')
        else:
            token = generate_confirmation_token(user.email)
            recover_url = url_for('reset_password_with_token', token=token, _external=True)
            html = render_template('recover_password.html', recover_url=recover_url)
            subject = 'Password reset requested'
            send_email(user.email, subject, html)
            flash('Password reset has been sent to your email.', 'info')

    return render_template('users/reset_password.html', form=form)


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_with_token(token):
    try:
        email = confirm_token(token)
    except Exception:
        abort(404)

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first_or_404()
        user.password = form.password.data
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('users/reset_password_with_token.html', form=form, token=token)


@app.route('/profile/update/<username>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def profile_update(username):
    user = User.query.filter_by(username=username).first()
    if not current_user.superuser:
        if current_user.get_id() != str(user.id):
            abort(404)
    form = UpdateProfileForm(obj=user)
    if form.validate_on_submit():
        avatar = form.avatar.data
        if avatar:
            import shutil
            filename = secure_filename(avatar.filename)
            avatar.save('/tmp/' + filename)
            size = os.stat('/tmp/' + filename).st_size
            if size > app.config['MAX_IMAGE_LENGTH']:
                form.avatar.errors.append('A file size must be < 5 mb')
            else:
                os.makedirs(os.path.join(app.config['UPLOAD_FOLDER']), exist_ok=True)
                path = app.config['UPLOAD_FOLDER'] + '/' + filename
                avatar.save(path)
                user.avatar = filename

        # TODO: refactor a validation 

        user.full_name = form.full_name.data
        db.session.commit()
        flash('A user account has been updated!', 'info')

    return render_template('users/profile_update.html', form=form, user=user)


@app.route('/profile/<username>')
@login_required
@check_confirmed
def profile_detail(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)

    return render_template('users/profile_detail.html', user=user)
