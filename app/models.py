from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils.types.choice import ChoiceType
from wtforms.widgets import HTMLString
from app import app, db, bcrypt


class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime, onupdate=db.func.now())


class User(Base):

    __tablename__ = 'users'

    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    superuser = db.Column(db.Boolean, nullable=False, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    _password = db.Column(db.Binary(128))
    issues = db.relationship('Issue', backref='user', lazy=True)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    def is_correct_password(self, plaintext):
        return bcrypt.check_password_hash(self._password, plaintext)

    @property
    def show_avatar(self):
        return HTMLString(
            f'<img height="30" width="30" src="/{app.config["UPLOAD_FOLDER"]}/{self.avatar}">'
            )

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return self.username


class Project(Base):

    __tablename__ = 'projects'

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text())
    issues = db.relationship('Issue', backref='project', lazy=True)

    @property
    def short_name(self):
        """
        Playing around short name
        """
        return '{}'.format(''.join([i for i in self.title if i == i.capitalize()]))

    def __repr__(self):
        return self.title


class Issue(Base):

    BUG = 'bug'
    PROPOSAL = 'proposal'
    TASK = 'task'
    ENCHENCEMENT = 'enchencement'

    KINDS = [
        (BUG, 'Bug'),
        (PROPOSAL, 'Proposal'),
        (TASK, 'Task'),
        (ENCHENCEMENT, 'Enchencement'),
    ]

    MINOR = 'minor'
    MAJOR = 'major'
    CRITICAL = 'critical'

    PRIORITIES = [
        (MINOR, 'Minor'),
        (MAJOR, 'Major'),
        (CRITICAL, 'Critical'),
    ]

    __tablename__ = 'issues'

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text())
    kind = db.Column(ChoiceType(KINDS))
    priority = db.Column(ChoiceType(PRIORITIES))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

    def __repr__(self):
        return f'{self.project.short_name}-{self.id}'


# class Attachment(Base):

#     __tablename__ = 'attachments'

#     object = 
#     project =
