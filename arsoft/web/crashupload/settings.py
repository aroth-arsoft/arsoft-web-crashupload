#!/usr/bin/python
# -*- coding: utf-8 -*-
# kate: space-indent on; indent-width 4; mixedindent off; indent-mode python;

# Django settings for arsoft.web.crashupload project.
from arsoft.web.utils import initialize_settings

# use initialize_settings from arsoft.web.utils to get the initial settings
# for a Django web application.
initialize_settings(__name__, __file__)

SITE_ID = 1

# Disable the host verification in the web application. This test must be
# done in the web server itself.
ALLOWED_HOSTS = ['*']

# Make this unique, and don't share it with anybody.
SECRET_KEY = '(l*vxapxd##_58l*-i@9g6%ao3xq53u6rs^sqf87*5q*9woswk'


