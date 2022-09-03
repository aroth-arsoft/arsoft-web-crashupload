#!/usr/bin/python
# -*- coding: utf-8 -*-
# kate: space-indent on; indent-width 4; mixedindent off; indent-mode python;

# Django settings for arsoft.web.crashupload project.
from arsoft.web.utils import initialize_settings
import os.path

# use initialize_settings from arsoft.web.utils to get the initial settings
# for a Django web application.
initialize_settings(__name__, __file__)

SITE_ID = 1

INSTALLED_APPS.insert(1, 'mozilla_django_oidc')  # Load after auth     

INSTALLED_APPS.extend(
    ['django.contrib.admin',
     'django_tables2',
     'django_tables2_column_shifter',
     'django_filters',
     "django_bootstrap5",
     ])

AUTHENTICATION_BACKENDS.append('mozilla_django_oidc.auth.OIDCAuthenticationBackend')

MIDDLEWARE.append('django.contrib.auth.middleware.AuthenticationMiddleware')
MIDDLEWARE.append('django.contrib.messages.middleware.MessageMiddleware')
MIDDLEWARE.append('mozilla_django_oidc.middleware.SessionRefresh')

in_docker = os.path.isfile('/.dockerenv')

LOGGING['loggers']['mozilla_django_oidc'] = {
    'handlers': ['console'] if in_docker else ['logfile'],
    #'level': 'ERROR' if not DEBUG else 'DEBUG',
    'level': 'DEBUG',
}

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(APP_DATA_DIR, 'crashupload.db')
    }
}


#DATABASES = {
    #'default': {
        #'ENGINE': 'django.db.backends.mysql',
        #'OPTIONS': {
            #'read_default_file': '/etc/mysql/my.cnf',
        #},
    #}
#}
# In my.cnf
#[client]
#database = blog_data
#user = djangouser
#password = your_actual_password
#default-character-set = utf8


# Make this unique, and don't share it with anybody.
SECRET_KEY = '(l*vxapxd##_58l*-i@9g6%ao3xq53u6rs^sqf87*5q*9woswk'

# Disable the host verification in the web application. This test must be
# done in the web server itself.
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = []
else:
    CSRF_TRUSTED_ORIGINS = CSRF_TRUSTED_ORIGINS.split(',')

# Application definition

MEDIA_ROOT = APP_DATA_DIR

APP_STYLE = os.getenv('APP_STYLE', 'crashdump.css')

NAV_ITEMS_JSON = os.getenv('NAV_ITEMS', '')

SHORT_DATETIME_FORMAT = 'Y-m-d H:i'
DATETIME_FORMAT = 'Y-m-d H:i'

MIGRATE_DB_DRIVER = os.getenv('MIGRATE_DB_DRIVER', 'MariaDB')
MIGRATE_DB_HOST = os.getenv('MIGRATE_DB_HOST', '127.0.0.1')
MIGRATE_DB_PORT = int(os.getenv('MIGRATE_DB_PORT', 3306))
MIGRATE_DB_DATABASE = os.getenv('MIGRATE_DB_DATABASE', 'trac')
MIGRATE_DB_USER = os.getenv('MIGRATE_DB_USER', 'root')
MIGRATE_DB_PASSWORD = os.getenv('MIGRATE_DB_PASSWORD', 'pass')

OIDC_RP_CLIENT_ID = os.getenv('OIDC_RP_CLIENT_ID', '')
OIDC_RP_CLIENT_SECRET = os.getenv('OIDC_RP_CLIENT_SECRET', '')


OIDC_BASE_URL = os.getenv('OIDC_BASE_URL', '')

# Check https://myurl/gitlab/.well-known/openid-configuration for endpoint URLs

OIDC_OP_AUTHORIZATION_ENDPOINT = os.getenv('OIDC_OP_AUTHORIZATION_ENDPOINT', OIDC_BASE_URL + '/oauth/authorize')
OIDC_OP_TOKEN_ENDPOINT = os.getenv('OIDC_OP_TOKEN_ENDPOINT', OIDC_BASE_URL + '/oauth/token')
OIDC_OP_USER_ENDPOINT = os.getenv('OIDC_OP_USER_ENDPOINT', OIDC_BASE_URL + '/oauth/userinfo')
OIDC_OP_JWKS_ENDPOINT = os.getenv('OIDC_OP_JWKS_ENDPOINT', OIDC_BASE_URL + '/oauth/discovery/keys')

# GitLab uses RS256, default is HS256
OIDC_RP_SIGN_ALGO = os.getenv('OIDC_RP_SIGN_ALGO', 'RS256')
OIDC_RP_SCOPES = os.getenv('OIDC_RP_SCOPES', 'openid email')

OIDC_CREATE_USER = bool(os.getenv('OIDC_CREATE_USER', 'True'))
OIDC_USERNAME_ALGO = 'arsoft.web.crashupload.oidc_generate_username'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
