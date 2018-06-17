from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, EqualTo


class RegisterForm(FlaskForm):

    username = StringField('Username*', validators=[DataRequired()])
    full_name = StringField('Full name*', validators=[DataRequired()])
    email = EmailField('Email*', validators=[DataRequired()])
    password = PasswordField(
        'Your password*',
        validators=[
            DataRequired(),
            EqualTo('confirm', message='Passwords should match')
            ])
    confirm = PasswordField('Confirm password*')


class LoginForm(FlaskForm):

    username = StringField('Username or email*', validators=[DataRequired()])
    password = PasswordField('Password*', validators=[DataRequired()])


class UserResetPasswordForm(FlaskForm):

    username = StringField('Your username or email*', validators=[DataRequired()])


class ResetPasswordForm(FlaskForm):

    password = PasswordField(
        'Your new password*',
        validators=[
            DataRequired(),
            EqualTo('confirm', message='Passwords should match')])
    confirm = PasswordField('Confirm password*')
