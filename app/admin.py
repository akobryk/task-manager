from flask import redirect, request, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.form import BaseForm
from flask_admin.form.upload import FileUploadField, ImageUploadField
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from app import app, db
from .models import User, Issue, Project


class MainAdminView(AdminIndexView):
    pass
#     def is_accessible(self):
#         return current_user.is_authenticated and current_user.superuser


class IssueAdmin(ModelView):
    form_excluded_columns = ['created_on', 'updated_on']
    form_choices = {
        'kind': Issue.KINDS,
        'priority': Issue.PRIORITIES
        }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.superuser

    def inaccessible_callback(self):
        return redirect(url_for('login', next=request.url))


class UserAdmin(ModelView):
    can_create = False
    column_list = (
        'show_avatar',
        'username',
        'email',
        'full_name',
        'confirmed',
        'superuser',
        'created_on',
        'updated_on',
        'confirmed_on',
        'last_login'
        )
    column_labels = {'show_avatar': 'Avatar'}
    form_columns = ('username', 'email', 'full_name', 'confirmed', 'superuser', 'avatar')

    form_overrides = {
        'avatar': ImageUploadField
    }

    form_args = {
        'avatar': {
            'base_path': app.config['UPLOAD_FOLDER'],
            'endpoint': 'get_media'
        }
    }

    def on_model_change(self, form, model, is_created):
        if model.confirmed_on is None and model.confirmed is True:
            model.confirmed_on = db.func.now()

    # def is_accessible(self):
    #     return current_user.is_authenticated and current_user.superuser

    # def inaccessible_callback(self):
    #     return redirect(url_for('login', next=request.url))


admin = Admin(app, index_view=MainAdminView(), name='Task Manager', template_mode='bootstrap3')
admin.add_view(ModelView(Project, db.session, name='Projects'))
admin.add_view(IssueAdmin(Issue, db.session, name='Issues'))
admin.add_view(UserAdmin(User, db.session, name='Users'))
