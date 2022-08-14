import django_tables2 as tables

#from django_tables2_column_shifter.tables import ColumnShiftTableBootstrap4 as ColumnShiftTable
from django_tables2_column_shifter.tables import ColumnShiftTableBootstrap5 as ColumnShiftTable

from .models import CrashDumpModel, CrashDumpState
from django.conf import settings
from packaging import version

class VersionNumberColumn(tables.Column):
    def render(self, record):
        return str(record)

class CrashDumpModelTable(ColumnShiftTable):
    class Meta:
        model = CrashDumpModel
        template_name = "django_tables2/bootstrap4.html"
        export_formats = ['csv', 'xlsx']
        fields = ('id', 
                    "state", "crashtimestamp", 'reporttimestamp',
                     "applicationName", 'applicationFile', 
                     'crashHostName', 'crashUserName', 
                     'reportHostName', 'reportUserName',
                     'productTargetVersion', 'productVersion', 
                     'machine_os', 'buildType')
        attrs = {"class": "crashlist table-sortable"}        
        hide_fields_by_default = [
            'reporttimestamp',
            'reportHostName', 'reportUserName',
            'applicationFile', 
            'productVersion', 
        ]

    id = tables.LinkColumn("crash_details", kwargs={"pk": tables.A("id")})
    machine_os = tables.Column(accessor='machineType', verbose_name='Machine')   
    crashtimestamp = tables.DateTimeColumn(format = settings.SHORT_DATETIME_FORMAT)
    reporttimestamp = tables.DateTimeColumn(format = settings.SHORT_DATETIME_FORMAT)

    productTargetVersion = tables.Column(accessor='productTargetVersion', verbose_name='Version')   

    #productVersionNum = VersionNumberColumn(accessor='productVersion')   
    #productTargetVersionNum = VersionNumberColumn(accessor='productTargetVersion')   


    def get_column_default_show(self):
        self.column_default_show = []
        for f in CrashDumpModelTable.Meta.fields:
            if not f in CrashDumpModelTable.Meta.hide_fields_by_default:
                self.column_default_show.append(f)
        return super(CrashDumpModelTable, self).get_column_default_show()

    def render_state(self, value):
        return value.name

    def render_applicationName(self, value, record):
        return record.get_applicationName()

    def render_id(self, value, record):
        return record.crashid

    def render_machine_os(self, value, record):
        return record.machineType + '/' + record.cpu_type + ' ' + record.osInfo

    def render_buildType(self, value, record):
        return record.buildType

    def render_productVersion(self, value, record):
        return version.Version(record.productVersion)

    def render_productTargetVersion(self, value, record):
        return version.Version(record.productTargetVersion)

