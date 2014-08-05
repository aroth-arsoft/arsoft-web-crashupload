from django.db import models
from django import forms
from django.core.urlresolvers import reverse 
import random
import string
import os
import urllib

class CrashDumpModel(models.Model):
    crashid = models.CharField('CrashId', max_length=36, unique=True, help_text='unique identifier of the crash')
    timestamp = models.DateTimeField('Timestamp', auto_now=True, auto_now_add=True)
    applicationName = models.CharField('ApplicationName', max_length=256, help_text='name of the application which caused the crash')
    applicationFile = models.CharField('ApplicationFile', max_length=512, help_text='file of the application which caused the crash')
    clientHostName = models.CharField('ClientHostName', max_length=256, help_text='full qualified host name of the client')
    clientUserName = models.CharField('ClientUserName', max_length=256, help_text='username of the client')

    productName = models.CharField('ProductName', max_length=256, help_text='name of the product')
    productVersion = models.CharField('ProductVersion', max_length=24, help_text='version of the product')
    productTargetVersion = models.CharField('ProductTargetVersion', max_length=24, help_text='target version of the product')
    buildType = models.CharField('BuildType', max_length=24, help_text='build type')
    buildPostfix = models.CharField('BuildPostfix', max_length=24, help_text='build postfix')

    machineType = models.CharField('MachineType', max_length=24, help_text='machine type')
    systemName = models.CharField('SystemName', max_length=24, help_text='name of operating system')
    osVersion = models.CharField('OSVersion', max_length=24, help_text='version of operating system')
    osRelease = models.CharField('OSRelease', max_length=24, help_text='release of operating system')
    osMachine = models.CharField('OSMachine', max_length=24, help_text='machine of operating system')

    class Meta:
        verbose_name = "Crash"
        verbose_name_plural = "Crashes"

    def __unicode__(self):
        return '%s (%s at %s)' % (self.id, self.applicationName, self.timestamp)
