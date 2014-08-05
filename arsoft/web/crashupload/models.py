from django.db import models

class CrashDumpModel(models.Model):
    crashid = models.CharField('Crash id', max_length=36, unique=True, help_text='unique identifier of the crash')
    timestamp = models.DateTimeField('Timestamp', auto_now=True, auto_now_add=True)
    applicationName = models.CharField('Application name', max_length=256, help_text='name of the application which caused the crash')
    applicationFile = models.CharField('Application file', max_length=512, help_text='file of the application which caused the crash')
    clientHostName = models.CharField('Client FQDN', max_length=256, null=True, help_text='full qualified host name of the client')
    clientUserName = models.CharField('Client user', max_length=256, null=True, help_text='username of the client')

    productName = models.CharField('Product name', max_length=256, help_text='name of the product')
    productVersion = models.CharField('Product version', max_length=24, help_text='version of the product')
    productTargetVersion = models.CharField('Product target version', max_length=24, help_text='target version of the product')

    DEBUG = 'DEBUG'
    RELWITHDEBINFO = 'RELWITHDEBINFO'
    RELEASE = 'RELEASE'
    MINSIZEREL = 'MINSIZEREL'
    BUILDTYPES = (
        (DEBUG, 'Debug'),
        (RELWITHDEBINFO, 'Release with debug info'),
        (RELEASE, 'Release'),
        (MINSIZEREL, 'Minimum size release'),
    )
    buildType = models.CharField('Build type', max_length=16, choices=BUILDTYPES, default=RELEASE, help_text='build type')
    buildPostfix = models.CharField('Build postfix', max_length=24, help_text='build postfix')

    machineType = models.CharField('Machine type', max_length=24, help_text='machine type')
    systemName = models.CharField('System name', max_length=24, help_text='name of operating system')
    osVersion = models.CharField('OS version', max_length=24, help_text='version of operating system')
    osRelease = models.CharField('OS release', max_length=24, help_text='release of operating system')
    osMachine = models.CharField('OS machine', max_length=24, help_text='machine of operating system')

    minidumpFile = models.CharField('Minidump file', max_length=256, null=True, help_text='relative path to the Minidump file')
    minidumpReportFile = models.CharField('Minidump report file', null=True, max_length=256, help_text='relative path to the Minidump report file')
    coredumpFile = models.CharField('Coredump file', max_length=256, null=True, help_text='relative path to the Coredump file')
    coredumpReportFile = models.CharField('Coredump report file', null=True, max_length=256, help_text='relative path to the Coredump report file')

    class Meta:
        verbose_name = "Crash"
        verbose_name_plural = "Crashes"

    def __unicode__(self):
        return '%s (%s at %s)' % (self.id, self.applicationName, self.timestamp)
