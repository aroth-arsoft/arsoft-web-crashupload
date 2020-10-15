import logging.config

import os
import signal
from flask import Flask, Blueprint, redirect, url_for, render_template, request

import settings
#from genetecwebapi.webapi import webapi
from api.genetec.endpoint import ns as genetec_namespace
from api.genetecevent.endpoint import ns as genetecevent_namespace
from api.restplus import api
import sync.genetecsync as gs

from genetecwebapi.webapi import init_app as genetec_init_app
from genetecwebapi.webapi import deinit_app as genetec_deinit_app
from reverse_proxy import ReverseProxyPrefixFix

#catch SIGTERM for graceful shutdown (and kill timer)
def handle_exit(sig, frame):
    print("signal: ", sig)
    raise(SystemExit)
signal.signal(signal.SIGTERM, handle_exit)

# derive from flask so we can close the timer thread on delete - seems not to work
#class FlaskWithDel(Flask):
#    def __init__(self, name):
#        print("init Flask")
#        Flask.__init__(self, name)

#    def __del__(self):
#        print("deinit Flask")
#        genetec_deinit_app()
        
#app = FlaskWithDel(__name__)

app = Flask(__name__)

def configure_app(flask_app):
    flask_app.config['DEBUG'] = settings.FLASK_DEBUG
    flask_app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP

    flask_app.config['GENETEC_HOSTNAME'] = settings.GENETEC_HOSTNAME

    try:
        flask_app.config['GENETEC_PORT'] = settings.GENETEC_PORT
    except:
        flask_app.config['GENETEC_PORT'] = 4590

    flask_app.config['GENETEC_USER'] = settings.GENETEC_USER
    flask_app.config['GENETEC_PASSWORD'] = settings.GENETEC_PASSWORD
    flask_app.config['GENETEC_APPID'] = settings.GENETEC_APPID

    try:
        flask_app.config['GENETEC_CERTIFICATE'] = settings.GENETEC_CERTIFICATE
    except:
        flask_app.config['GENETEC_CERTIFICATE'] = None

    try:
        flask_app.config['GENETEC_TIMEOUT'] = settings.GENETEC_TIMEOUT
    except:
        flask_app.config['GENETEC_TIMEOUT'] = 12

    try:
        flask_app.config['GENETEC_HTTPS'] = settings.GENETEC_HTTPS
    except:
        flask_app.config['GENETEC_HTTPS'] = False

    try:
        flask_app.config['GENETEC_VERIFY_CERTIFICATE'] = settings.GENETEC_VERIFY_CERTIFICATE
    except:
        flask_app.config['GENETEC_VERIFY_CERTIFICATE'] = False

#VMS settings
    try:
        flask_app.config['GENETEC_VMS_READEVENTS'] = settings.GENETEC_VMS_READEVENTS
    except:
        flask_app.config['GENETEC_VMS_READEVENTS'] = False

    try:
        flask_app.config['GENETEC_VMS_HOSTNAME'] = settings.GENETEC_VMS_HOSTNAME
    except:
        flask_app.config['GENETEC_VMS_HOSTNAME'] = flask_app.config['GENETEC_HOSTNAME']

    try:
        flask_app.config['GENETEC_VMS_PORT'] = settings.GENETEC_VMS_PORT
    except:
        flask_app.config['GENETEC_VMS_PORT'] = flask_app.config['GENETEC_PORT']

    try:
        flask_app.config['GENETEC_VMS_USER'] = settings.GENETEC_VMS_USER
    except:
        flask_app.config['GENETEC_VMS_USER'] = flask_app.config['GENETEC_USER']

    try:
        flask_app.config['GENETEC_VMS_PASSWORD'] = settings.GENETEC_VMS_PASSWORD
    except:
        flask_app.config['GENETEC_VMS_PASSWORD'] = flask_app.config['GENETEC_PASSWORD']

    try:
        flask_app.config['GENETEC_VMS_APPID'] = settings.GENETEC_VMS_APPID
    except:
        flask_app.config['GENETEC_VMS_APPID'] = flask_app.config['GENETEC_APPID']

    try:
        flask_app.config['GENETEC_VMS_CERTIFICATE'] = settings.GENETEC_VMS_CERTIFICATE
    except:
        flask_app.config['GENETEC_VMS_CERTIFICATE'] = flask_app.config['GENETEC_CERTIFICATE']

    try:
        flask_app.config['GENETEC_VMS_HTTPS'] = settings.GENETEC_VMS_HTTPS
    except:
        flask_app.config['GENETEC_VMS_HTTPS'] = flask_app.config['GENETEC_HTTPS']

    try:
        flask_app.config['GENETEC_VMS_VERIFY_CERTIFICATE'] = settings.GENETEC_VMS_VERIFY_CERTIFICATE
    except:
        flask_app.config['GENETEC_VMS_VERIFY_CERTIFICATE'] = flask_app.config['GENETEC_VERIFY_CERTIFICATE']

# Automatically forward to API page; avoid empty main page
@app.route('/')
def index():
    return redirect('/sync')
#    return render_template('sync.html')

@app.route('/sync')
def sync_page():
    return gs.genetec_sync_page()

@app.route('/doors', methods=['GET', 'POST'])
def doors_page():
    return gs.genetec_doors_page(request)

@app.route('/door/<string:id>', methods=['GET', 'POST'])
def door_edit_page(id):
    return gs.genetec_door_edit_page(request, id)

@app.route('/doorsearch/<string:id>', methods=['POST'])
def door_edit_page_search(id):
    return gs.genetec_door_edit_page(request, id, True)

@app.route('/doordelete/<string:id>', methods=['POST'])
def door_edit_page_delete(id):
    return gs.genetec_door_delete(request, id)

@app.route('/log')
def log_page():
    return gs.genetec_log_page()

@app.route('/sync_oracle_to_local')
def sync_oracle_to_local():
    return gs.sync_oracle_to_local()

@app.route('/sync_oracle_to_local_days/<int:d>')
def sync_oracle_to_local_days(d):
    return gs.sync_oracle_to_local_days(d)

@app.route('/sync_oracle_to_local_all')
def sync_oracle_to_local_all():
    return gs.sync_oracle_to_local_all()

@app.route('/sync_local_to_genetec')
def sync_local_to_genetec():
    return gs.sync_local_to_genetec()

@app.route('/sync_genetec_to_local')
def sync_genetec_to_local():
    return gs.sync_genetec_to_local()

@app.route('/sync_cancel')
def sync_cancel():
    return gs.sync_cancel()

@app.route('/update_doors')
def update_doors():
    return gs.update_doors()

def initialize_app(flask_app, use_development_server=False):
    if use_development_server:
        logging_conf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'logging.conf'))
        logging.config.fileConfig(logging_conf_path)

        global log
        log = logging.getLogger(__name__)

    configure_app(flask_app)

    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    #api.add_namespace(genetec_namespace)
    #api.add_namespace(genetecevent_namespace)
    flask_app.register_blueprint(blueprint)

    genetec_init_app(flask_app)

def main():
    initialize_app(app, use_development_server=True)
    log.info('>>>>> Starting development server at http://{}/api/ <<<<<'.format(app.config['SERVER_NAME']))
    app.run(host='0.0.0.0',port=settings.FLASK_SERVER_PORT,debug=settings.FLASK_DEBUG)
    genetec_deinit_app()


if os.getenv('SERVER_SOFTWARE', ''):
    # assume running in gunicorn (or compatible wsgi server)
    initialize_app(app)
    app = ReverseProxyPrefixFix(app)
elif __name__ == "__main__":
    main()
