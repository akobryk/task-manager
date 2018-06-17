from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user, login_required


def check_confirmed(func):

    @wraps(func)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.confirmed is False:
            flash('Please confirm your account!')
            return redirect(url_for('unconfirmed'))
        return func(*args, **kwargs)

    return decorated_function
