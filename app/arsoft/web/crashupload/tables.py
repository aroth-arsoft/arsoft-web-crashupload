import django_tables2 as tables
from .models import CrashDumpModel, CrashDumpState

class CrashDumpModelTable(tables.Table):
    class Meta:
        model = CrashDumpModel
        template_name = "django_tables2/bootstrap.html"
        fields = ('id', "state", "crashtimestamp", "applicationName", 'applicationFile', 'crashHostName', 'crashUserName', 'productVersion', 'machine_os', 'buildType')
        attrs = {"class": "properties table-sortable"}        

    id = tables.LinkColumn("crash_details", kwargs={"pk": tables.A("id")})
    machine_os = tables.Column(accessor='machineType')   

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
