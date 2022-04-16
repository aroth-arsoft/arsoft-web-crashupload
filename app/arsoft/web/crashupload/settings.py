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

INSTALLED_APPS.extend(
    ['django.contrib.admin',
     'django_tables2',
     'django_tables2_column_shifter',
     'django_filters',
     'bootstrap4',
     ])
MIDDLEWARE.append('django.contrib.auth.middleware.AuthenticationMiddleware')

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
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')

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
