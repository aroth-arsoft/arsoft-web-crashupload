from django.db import models

print('models')

class CrashDumpState(models.Model):
    name = models.CharField('Name', max_length=32, help_text='short name of the state')
    description = models.CharField('Description', max_length=256, help_text='description of the attachment')

    class Meta:
        verbose_name = "Crash state"
        verbose_name_plural = "Crash states"

class CrashDumpModel(models.Model):
    crashid = models.CharField('Crash id', max_length=36, unique=True, help_text='unique identifier of the crash')
    state = models.ForeignKey(CrashDumpState, on_delete=models.CASCADE)
    timestamp = models.DateTimeField('Timestamp', auto_now_add=True)
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

    POSTFIX_NONE = ''
    POSTFIX_DEBUG = 'd'
    POSTFIX_RELEASE = 'r'
    POSTFIX_MINSIZEREL = 'rs'
    POSTFIX_RELWITHDEBINFO = 'rd'
    POSTFIXES = (
        (POSTFIX_NONE, 'None (release)'),
        (POSTFIX_DEBUG, 'Debug'),
        (POSTFIX_RELWITHDEBINFO, 'Release with debug info'),
        (POSTFIX_RELEASE, 'Release'),
        (POSTFIX_MINSIZEREL, 'Minimum size release'),
    )
    buildPostfix = models.CharField('Build postfix', max_length=4, choices=POSTFIXES, default=POSTFIX_NONE, help_text='build postfix')

    MACHINE_TYPE_UNKNOWN = 'unknown'
    MACHINE_TYPE_PC = 'PC'
    MACHINE_TYPE_MAC = 'Mac'
    MACHINE_TYPE_VIRTUALBOX = 'VirtualBox'
    MACHINE_TYPE_VMWARE = 'VMWare'
    MACHINE_TYPE_VPC = 'VPC'
    MACHINE_TYPES = (
        (MACHINE_TYPE_UNKNOWN, 'Unknown'),
        (MACHINE_TYPE_PC, 'PC'),
        (MACHINE_TYPE_MAC, 'Mac'),
        (MACHINE_TYPE_VIRTUALBOX, 'VirtualBox'),
        (MACHINE_TYPE_VMWARE, 'VMWare'),
        (MACHINE_TYPE_VPC, 'Virtual PC'),
    )
    machineType = models.CharField('Machine type', max_length=16, choices=MACHINE_TYPES, default=MACHINE_TYPE_UNKNOWN, help_text='machine type')

    systemName = models.CharField('System name', max_length=24, help_text='name of operating system')
    osVersion = models.CharField('OS version', max_length=24, help_text='version of operating system')
    osRelease = models.CharField('OS release', max_length=24, help_text='release of operating system')
    osMachine = models.CharField('OS machine', max_length=24, help_text='machine of operating system')

    systemInfoData = models.TextField('System info', max_length=65536, null=True, help_text='system information')
    gfxCapsFile = models.CharField('GfxCaps file', max_length=256, null=True, help_text='relative path to the gfxcaps file')
    minidumpFile = models.CharField('Minidump file', max_length=256, null=True, help_text='relative path to the Minidump file')
    minidumpReportTextFile = models.CharField('Minidump text report file', null=True, max_length=256, help_text='relative path to the Minidump text report file')
    minidumpReportXMLFile = models.CharField('Minidump XML report file', null=True, max_length=256, help_text='relative path to the Minidump XML report file')
    minidumpReportHTMLFile = models.CharField('Minidump HTML report file', null=True, max_length=256, help_text='relative path to the Minidump HTML report file')
    coredumpFile = models.CharField('Coredump file', max_length=256, null=True, help_text='relative path to the Coredump file')
    coredumpReportTextFile = models.CharField('Coredump text report file', null=True, max_length=256, help_text='relative path to the Coredump text report file')
    coredumpReportXMLFile = models.CharField('Coredump XML report file', null=True, max_length=256, help_text='relative path to the Coredump XML report file')
    coredumpReportHTMLFile = models.CharField('Coredump HTML report file', null=True, max_length=256, help_text='relative path to the Coredump HTML report file')

    class Meta:
        verbose_name = "Crash"
        verbose_name_plural = "Crashes"

    def __unicode__(self):
        return '%s (%s at %s)' % (self.id, self.applicationName, self.timestamp)

class CrashDumpAttachment(models.Model):
    crash = models.ForeignKey(CrashDumpModel, on_delete=models.CASCADE)
    name = models.CharField('Name', max_length=256, help_text='name of the attachment')
    description = models.TextField('Description', max_length=8192, help_text='description of the attachment')
    storageFile = models.CharField('Storage file', max_length=256, help_text='path to the stored attachment file')

    class Meta:
        verbose_name = "Crash attachment"
        verbose_name_plural = "Crash attachments"

class CrashDumpLink(models.Model):
    crash = models.ForeignKey(CrashDumpModel, on_delete=models.CASCADE)
    name = models.CharField('Name', max_length=256, null=True, help_text='name of the link')
    url = models.TextField('URL', max_length=2048, help_text='URL')

    class Meta:
        verbose_name = "Crash link"
        verbose_name_plural = "Crash links"
