#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='arsoft-web-crashupload',
		version='1.0.0',
		description='upload crash reports',
		author='Andreas Roth',
		author_email='aroth@arsoft-online.com',
		url='http://www.arsoft-online.com/',
		packages=['arsoft.web.crashupload'],
		scripts=[],
		data_files=[
            ('/etc/arsoft/web/crashupload/static', ['arsoft/web/crashupload/static/main.css']),
            ('/etc/arsoft/web/crashupload/templates', ['arsoft/web/crashupload/templates/home.html']),
            ]
		)
