from django.contrib import admin
from django import forms
from arsoft.web.crashupload.models import CrashDumpModel

class CrashDumpModelForm(forms.ModelForm):
    class Meta:
        model = CrashDumpModel

class CrashDumpModelAdmin(admin.ModelAdmin):
    list_display = ('crashid', 'applicationName', 'clientHostName', 'clientUserName', 'productName', 'productVersion')
    fields = ['crashid',
            'applicationFile', 'applicationName',
            'clientHostName', 'clientUserName',
            'productName', 'productVersion', 'productTargetVersion',
            'buildType', 'buildPostfix',
            'machineType', 'systemName',
            'osVersion', 'osRelease', 'osMachine'
            ]
    form = CrashDumpModelForm

admin.site.register(CrashDumpModel, CrashDumpModelAdmin)
