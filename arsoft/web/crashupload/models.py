from django.db import models, migrations

class CrashDumpState(models.Model):
    name = models.CharField('Name', max_length=32, help_text='short name of the state')
    description = models.CharField('Description', max_length=256, help_text='description of the attachment')

    class Meta:
        verbose_name = "Crash state"
        verbose_name_plural = "Crash states"

class CrashDumpModel(models.Model):

    @staticmethod
    def uuid_is_valid(uuid):
        if isinstance(uuid, UUID):
            return True
        else:
            try:
                UUID(uuid)
                return True
            except:
                return False

    crashid = models.CharField('Crash id', max_length=36, unique=True, help_text='unique identifier of the crash')
    state = models.ForeignKey(CrashDumpState, on_delete=models.CASCADE)
    crashtimestamp = models.DateTimeField('Crash Timestamp', auto_now_add=True)
    reporttimestamp = models.DateTimeField('Report Timestamp', auto_now_add=True)

    applicationName = models.CharField('Application name', max_length=256, help_text='name of the application which caused the crash')
    applicationFile = models.CharField('Application file', max_length=512, help_text='file of the application which caused the crash')
    reportHostName = models.CharField('Report FQDN', max_length=256, null=True, help_text='full qualified host name of the reporter')
    reportUserName = models.CharField('Report user', max_length=256, null=True, help_text='username of the reporter')

    crashHostName = models.CharField('Crash FQDN', max_length=256, null=True, help_text='full qualified host name of the crash application')
    crashUserName = models.CharField('Crash user', max_length=256, null=True, help_text='username of the crash application')

    productName = models.CharField('Product name', max_length=256, help_text='name of the product')
    productCodeName = models.CharField('Product code name', max_length=256, help_text='code name of the product')
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

    CPU_TYPE_UNKNOWN = -1
    CPU_TYPE_X86 = 0
    CPU_TYPE_MIPS = 1
    CPU_TYPE_ALPHA = 2
    CPU_TYPE_POWERPC = 3
    CPU_TYPE_SHX = 4
    CPU_TYPE_ARM = 5
    CPU_TYPE_IA64 = 6
    CPU_TYPE_ALPHA64 = 7
    CPU_TYPE_MSIL = 8
    CPU_TYPE_AMD64 = 9
    CPU_TYPE_X64_WIN64 = 10
    CPU_TYPE_SPARC = 11
    CPU_TYPE_POWERPC64 = 12
    CPU_TYPE_ARM64 = 13
    CPU_TYPES = (
        (CPU_TYPE_UNKNOWN, 'Unknown'),
        (CPU_TYPE_X86, 'x86'),
        (CPU_TYPE_MIPS, 'MIPS'),
        (CPU_TYPE_ALPHA, 'Alpha'),
        (CPU_TYPE_POWERPC, 'PowerPC'),
        (CPU_TYPE_SHX, 'SHX'),
        (CPU_TYPE_ARM, 'ARM'),
        (CPU_TYPE_IA64, 'IA64'),
        (CPU_TYPE_ALPHA64, 'Alpha64'),
        (CPU_TYPE_MSIL, 'MSIL'),
        (CPU_TYPE_AMD64, 'AMD64'),
        (CPU_TYPE_X64_WIN64, 'x64 Win64'),
        (CPU_TYPE_SPARC, 'SPARC'),
        (CPU_TYPE_POWERPC64, 'PowerPC 64'),
        (CPU_TYPE_ARM64, 'ARM64'),
    )
    cpuType = models.IntegerField('CPU type', choices=CPU_TYPES, default=CPU_TYPE_UNKNOWN, help_text='CPU type')

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

    uuid = property(lambda self: self.crashid)
    exists = property(lambda self: self.crashid is not None)

    has_minidump = property(lambda self: self.minidumpFile or self.minidumpReportTextFile or self.minidumpReportXMLFile or self.minidumpReportHTMLFile)
    has_coredump = property(lambda self: self.coredumpFile or self.coredumpReportTextFile or self.coredumpReportXMLFile or self.coredumpReportHTMLFile)

    @property
    def is_64_bit(self):
        if self.cpuType == CrashDumpModel.CPU_TYPE_X86 or \
            self.cpuType == CrashDumpModel.CPU_TYPE_MIPS or \
            self.cpuType == CrashDumpModel.CPU_TYPE_ALPHA or \
            self.cpuType == CrashDumpModel.CPU_TYPE_POWERPC or \
            self.cpuType == CrashDumpModel.CPU_TYPE_SHX or \
            self.cpuType == CrashDumpModel.CPU_TYPE_ARM or \
            self.cpuType == CrashDumpModel.CPU_TYPE_SPARC or \
            self.cpuType == CrashDumpModel.CPU_TYPE_MSIL:
            return False
        elif self.cpuType == CrashDumpModel.CPU_TYPE_ALPHA64 or \
            self.cpuType == CrashDumpModel.CPU_TYPE_IA64 or \
            self.cpuType == CrashDumpModel.CPU_TYPE_AMD64 or \
            self.cpuType == CrashDumpModel.CPU_TYPE_X64_WIN64 or \
            self.cpuType == CrashDumpModel.CPU_TYPE_POWERPC64 or \
            self.cpuType == CrashDumpModel.CPU_TYPE_ARM64:
            return True
        else:
            return False

    class Meta:
        verbose_name = "Crash"
        verbose_name_plural = "Crashes"

    def __unicode__(self):
        return '%s (%s at %s)' % (self.id, self.applicationName, self.timestamp)

    def get_applicationName(self):
        a = self.applicationName
        if a is None:
            return None
        slash = a.rfind('/')
        backslash = a.rfind('\\')
        if slash > backslash:
            return a[slash+1:]
        elif backslash > 0:
            return a[backslash+1:]
        else:
            return a

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


def add_crashdump_states(apps, schema_editor):
    model = apps.get_model('crashupload', 'CrashDumpState')
    uploaded = model.objects.create(name='uploaded', description='Newly uploaded crash')

class Migration(migrations.Migration):

    dependencies = [
        ('crashupload', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_crashdump_states),
    ]
