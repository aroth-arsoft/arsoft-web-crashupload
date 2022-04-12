from django.template import RequestContext, loader
from django.urls import reverse
from django.http import HttpResponseServerError, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import MySQLdb
import MySQLdb.cursors
from arsoft.web.crashupload.views import crash_new_issue_link


import logging

from .models import CrashDumpLink, CrashDumpModel, CrashDumpState

logger = logging.getLogger(__name__)

class MigrateDb:

    def __init__(self, settings):
        cfg = {
            'DRIVER':settings.MIGRATE_DB_DRIVER,
            'HOST':settings.MIGRATE_DB_HOST,
            'PORT':settings.MIGRATE_DB_PORT,
            'DATABASE':settings.MIGRATE_DB_DATABASE,
            'USER':settings.MIGRATE_DB_USER,
            'PASSWORD':settings.MIGRATE_DB_PASSWORD
            }
        self.open(cfg)

    def __deinit__(self):
        self.close()

    def open(self, settings):
        self.SQL_DATEFORMAT = "%Y-%m-%dT%H:%M:%S"

        encoding = 'utf8'
        self.is_mysql = 'MariaDB' in settings['DRIVER']
        if self.is_mysql:
            self.cnxn=MySQLdb.connect(
                host=settings['HOST'],port=settings['PORT'],user=settings['USER'],password=settings['PASSWORD'],database=settings['DATABASE'],
                cursorclass=MySQLdb.cursors.DictCursor)
        else:
            raise NotImplementedError
            # self.cnxn = pyodbc.connect(f"DRIVER={{{settings['DRIVER']}}};Server={settings['HOST']};Port={settings['PORT']};Database={settings['DATABASE']};UID={settings['USER']};PWD={settings['PASSWORD']};CHARSET=UTF8")
            # self.cnxn.setdecoding(pyodbc.SQL_CHAR, encoding=encoding)
            # self.cnxn.setdecoding(pyodbc.SQL_WCHAR, encoding=encoding)
            # self.cnxn.setencoding(encoding=encoding)

        self.cursor = self.cnxn.cursor()
        self.cursor2 = self.cnxn.cursor()

        if not self.is_mysql:
            self.GET_LAST_INSERTED_ID = 'SELECT SCOPE_IDENTITY();' #MSSQL
        else:
            self.GET_LAST_INSERTED_ID = 'SELECT LAST_INSERT_ID()'  #MYSQL
        
    def getinfo(self):
        return self.info

    def close(self):
        if self.cnxn:
            self.cnxn.commit()
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.cursor2:
            self.cursor2.close()
            self.cursor2 = None
        if self.cnxn:
            self.cnxn.close()
            self.cnxn = None

class MigrateField(object):
    def __init__(self, name=None, skip=False) -> None:
        super().__init__()
        self.name = name
        self.skip = skip

    def convert(self, value):
        return value

class MigrateStateField(MigrateField):
    _crashdumpstate_map = {}
    def convert(self, value):
        if not MigrateStateField._crashdumpstate_map:
            MigrateStateField._crashdumpstate_map = {}
            for s in CrashDumpState.objects.all():
                MigrateStateField._crashdumpstate_map[s.name] = s
        return MigrateStateField._crashdumpstate_map.get(value, None)

def _sql_query_fields(fields):
    ret = ''
    for k,v in fields.items():
        if ret:
            ret += ','
        ret += '`' + k + '`'
    return ret

def _sql_to_model(fields, record):
    ret = {}
    for k,v in fields.items():
        if v is None:
            #ret[k] = record.get(k)
            continue
        elif isinstance(v, MigrateField):
            if v.skip:
                continue
            raw = record.get(k)
            value = v.convert(raw)
            ret[v.name if v.name else k] = value
    if ret.get('applicationName') is None:
        f = ret.get('applicationFile')
        ret['applicationName'] = f
    return ret

@csrf_exempt
def migrate(request):
    from django.conf import settings

    try:
        db = MigrateDb(settings)
    except MySQLdb.Error as e:
        body = "Failed to connect to database: " + str(e)
        return HttpResponse(body, status=500, content_type="text/plain")

    file = None
    error_message = None

    crashdump_fields = {
        'id':MigrateField(skip=True), 
        'uuid':MigrateField('crashid'), 
        'type':MigrateField(skip=True), 
        'status':MigrateStateField('state'), 
        'priority':MigrateField(skip=True), 
        'severity':MigrateField(skip=True), 
        'owner':MigrateField(skip=True), 
        'reporter':MigrateField(skip=True), 
        'cc':MigrateField(skip=True), 
        'component':MigrateField(skip=True), 
        'milestone':MigrateField(skip=True), 
        'version':MigrateField(skip=True), 
        'resolution':MigrateField(skip=True), 
        'summary':MigrateField(skip=True), 
        'description':MigrateField(skip=True), 
        'keywords':MigrateField(skip=True), 
        'crashtime':MigrateField('crashtimestamp'), 
        'reporttime':MigrateField('reporttimestamp'), 
        'uploadtime':MigrateField(skip=True), 
        'changetime':MigrateField(skip=True), 
        'closetime':MigrateField(skip=True), 
        'applicationname':MigrateField('applicationName'), 
        'applicationfile':MigrateField('applicationFile'), 
        'uploadhostname':MigrateField('reportHostName'), 
        'uploadusername':MigrateField('reportUserName'), 
        'crashhostname':MigrateField('crashHostName'), 
        'crashusername':MigrateField('crashUserName'), 
        'productname':MigrateField('productName'), 
        'productcodename':MigrateField('productCodeName'), 
        'productversion':MigrateField('productVersion'),  
        'producttargetversion':MigrateField('productTargetVersion'), 
        'buildtype':MigrateField('buildType'), 
        'buildpostfix':MigrateField('buildPostfix'),  
        'machinetype':MigrateField('machineType'),  
        'systemname':MigrateField('systemName'),  
        'osversion':MigrateField('osVersion'),  
        'osrelease':MigrateField('osRelease'),  
        'osmachine':MigrateField('osMachine'),  
        'minidumpfile':MigrateField('minidumpFile'),  
        'minidumpreporttextfile':MigrateField('minidumpReportTextFile'),  
        'minidumpreportxmlfile':MigrateField('minidumpReportXMLFile'),  
        'minidumpreporthtmlfile':MigrateField('minidumpReportHTMLFile'),  
        'coredumpfile':MigrateField('coredumpFile'),  
        'coredumpreporttextfile':MigrateField('coredumpReportTextFile'),  
        'coredumpreportxmlfile':MigrateField('coredumpReportXMLFile'),  
        'coredumpreporthtmlfile':MigrateField('coredumpReportHTMLFile'),  
    }
    crashdump_ticket_fields = {
        'crash':MigrateField('crash'), 
        'ticket':MigrateField('ticket'), 
    }

    num_records = 0
    num_new_records = 0
    num_new_tickets = 0
    try:
        new_state = CrashDumpState.objects.filter(name='new')
        if new_state:
            new_state = new_state[0]
        else:
            return HttpResponseServerError('CrashDumpState new missing')
            
        db.cursor.execute(f"select " + _sql_query_fields(crashdump_fields) + " from crashdump")
        for item in db.cursor.fetchall():
            num_records += 1
            existing = CrashDumpModel.objects.filter(crashid=item['uuid'])
            if not existing:
                newcrash = CrashDumpModel(**_sql_to_model(crashdump_fields, item))
                if newcrash.state is None:
                    newcrash.state = new_state
                newcrash.save()
                num_new_records += 1
            else:
                newcrash = existing[0]

            existing_links = CrashDumpLink.objects.filter(crash=newcrash.id)

            db.cursor2.execute(f"select " + _sql_query_fields(crashdump_ticket_fields) + " from crashdump_ticket where crash=%s", ( item['id'], ))
            for link_item in db.cursor2.fetchall():
                num_records += 1
                issue_name = 'Crash %i' % link_item['ticket']
                found = False
                for e in existing_links:
                    if e.name == issue_name:
                        found = True
                if not found:
                    link_obj, error = crash_new_issue_link(request, newcrash)
                    if link_obj:
                        num_new_tickets += 1

    except MySQLdb.Error as e:
        return HttpResponseServerError('MySQL Error %s' % e)

    except TypeError as ex:
        return HttpResponseServerError('Type Error %s' % ex)
  

    body = "%i crashes found, %i new crashes, %i new tickets imported" % (num_records, num_new_records, num_new_tickets)
    return HttpResponse(body, status=200, content_type="text/plain")
