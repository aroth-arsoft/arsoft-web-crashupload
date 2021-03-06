from django.contrib import admin
from django import forms
from arsoft.web.crashupload.models import CrashDumpState, CrashDumpModel

class CrashDumpStateForm(forms.ModelForm):
    class Meta:
        model = CrashDumpState
        fields = '__all__'

class CrashDumpStateAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    fields = ['name', 'description']
    form = CrashDumpStateForm

class CrashDumpModelForm(forms.ModelForm):
    class Meta:
        model = CrashDumpModel
        fields = '__all__'

class CrashDumpModelAdmin(admin.ModelAdmin):
    list_display = ('crashid', 'crashtimestamp', 'reporttimestamp', 'applicationName', 
        'reportHostName', 'reportUserName', 'crashHostName', 'crashUserName', 
        'productName', 'productCodeName', 'productVersion')

    fields = ['crashid',
            'applicationFile', 'applicationName',
            'reportHostName', 'reportUserName', 'crashHostName', 'crashUserName', 
            'productName', 'productCodeName', 'productVersion', 'productTargetVersion',
            'buildType', 'buildPostfix',
            'machineType', 'systemName',
            'osVersion', 'osRelease', 'osMachine'
            ]
    form = CrashDumpModelForm

admin.site.register(CrashDumpState, CrashDumpStateAdmin)
admin.site.register(CrashDumpModel, CrashDumpModelAdmin)

