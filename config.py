import os

DEBUG = False
TESTING = False
ENV = 'production'
SECRET_KEY = b'\xad\x9d\xbf\x93|\xd3\xab\x81\x14Z\xd0\xfb\xd6-\xd4\x84'
SECURITY_PASSWORD_SALT = 'this_is_password_salt'
UPLOAD_FOLDER = os.path.join('media')

try:
    from local_config import *  # noqa
except ImportError:
    pass
