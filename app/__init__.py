from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from werkzeug import SharedDataMiddleware

app = Flask(__name__)
app.config.from_object('config')
app.debug = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.add_url_rule('/media/<filename>', 'get_media',
                 build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/media':  app.config['UPLOAD_FOLDER']
})

from .models import User  # noqa


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


from . import views, models, manage  # noqa
