from datetime import datetime
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from .models import User
from .forms import RegisterForm, LoginForm
from .utils import send_email, generate_confirmation_token, confirm_token


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        check_username = User.query.filter_by(username=form.username.data).first()
        print(check_username)
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
            html = render_template('activate_account.html', confirm_url=confirm_url)
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
