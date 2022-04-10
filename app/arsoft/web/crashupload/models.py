from pickle import NONE
from crashdump.utils import format_os_version_short, get_os_version_number, get_os_build_number
from django.db import models, migrations
from django.urls import reverse

class CrashDumpSetting(models.Model):
    id = models.AutoField(primary_key=True)

    AVAILABLE_SETTINGS = (
        ('issue_title', 'issue_title'),
        ('issue_description', 'issue_description'),
        ('issue_labels', 'issue_labels'),
        ('max_upload_size', 'max_upload_size'),
        ('upload_disabled', 'upload_disabled'),
    )
    name = models.CharField('Name', unique=True, choices=AVAILABLE_SETTINGS, max_length=64, help_text='Name')
    value = models.CharField('Value', max_length=1024, help_text='Value') 

    class Meta:
        verbose_name = "Setting"
        verbose_name_plural = "Settings"

    @staticmethod
    def get(key,default_value=None):
        try:
            s = CrashDumpSetting.objects.get(name=key)
        except CrashDumpSetting.DoesNotExist:
            s = None
        if s:
            return s.value
        else:
            return default_value

class CrashDumpProject(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('Name', max_length=32, help_text='Project name')
    description = models.CharField('Description', max_length=256, help_text='description of the project')
    url = models.CharField('Url', max_length=256, null=True, default=None, help_text='URL for the Project page')

    GITLAB = 'GitLab'
    ISSUETRACKERTYPES = (
        (None, 'None'),
        (GITLAB, 'GitLab'),
    )
    issueTrackerType = models.CharField('Issue Tracker', max_length=16, choices=ISSUETRACKERTYPES, null=True, default=None, help_text='Issue Tracker')
    issueTrackerUrl = models.CharField('Issue Tracker Url', max_length=256, null=True, default=None, help_text='URL to the issue tracker') 
    issueTrackerToken = models.CharField('Issue Tracker Token', max_length=256, null=True, default=None, help_text='Token to access the issue tracker') 

    codename = models.CharField('Code name', max_length=256, default=None, help_text='Code name of the project for crash matching')

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    @staticmethod
    def findByCodename(codename):
        q = CrashDumpProject.objects.filter(codename=codename)
        if q:
            return q[0]
        else:
            return None
        

class CrashDumpState(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('Name', max_length=32, help_text='short name of the state')
    description = models.CharField('Description', max_length=256, help_text='description of the state')

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

    id = models.AutoField(primary_key=True)
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
    productCodeName = models.CharField('Code name', max_length=256, help_text='code name of the product')
    productVersion = models.CharField('Product version', max_length=24, help_text='version of the product')
    productTargetVersion = models.CharField('Target version', max_length=24, help_text='target version of the product')

    DEBUG = 'DEBUG'
    RELWITHDEBINFO = 'RELWITHDEBINFO'
    RELEASE = 'RELEASE'
    MINSIZEREL = 'MINSIZEREL'
    BUILDTYPES = (
        (DEBUG, 'DEBUG'),
        (RELWITHDEBINFO, 'RELWITHDEBINFO'),
        (RELEASE, 'RELEASE'),
        (MINSIZEREL, 'MINSIZEREL'),
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
    
    @property
    def cpu_type(self):
        cpuType = self.cpuType
        if cpuType == CrashDumpModel.CPU_TYPE_UNKNOWN:
            if self.osMachine == 'amd64' or self.osMachine == 'x86_64':
                cpuType = CrashDumpModel.CPU_TYPE_AMD64
            elif self.osMachine == 'x86':
                cpuType = CrashDumpModel.CPU_TYPE_X86

        if cpuType != CrashDumpModel.CPU_TYPE_UNKNOWN:
            return CrashDumpModel.CPU_TYPES[cpuType + 1][1]
        else:
            return 'Unknown'

    systemName = models.CharField('System name', max_length=24, help_text='name of operating system')
    osVersion = models.CharField('OS version', max_length=24, help_text='version of operating system')
    osRelease = models.CharField('OS release', max_length=24, help_text='release of operating system')
    os_version_number = property(lambda self: get_os_version_number(self.platform_type, self.osVersion, self.osRelease) )
    os_build_number = property(lambda self: get_os_build_number(self.platform_type, self.osVersion, self.osRelease) )
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
    def platform_type(self):
        if self.systemName == 'Linux':
            return self.systemName
        elif self.systemName != 'Windows NT' and self.systemName.startswith('Windows'):
            return 'Windows NT'
        else:
            return self.systemName

    @property
    def osInfo(self):
        return format_os_version_short(self.platform_type, self.os_version_number, self.os_build_number)

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

    @property
    def url(self):
        local_url = reverse('crash_details', args=[self.id])
        return local_url

    def to_json(self):
        return {'id': self.id, 'uuid': self.uuid, 'state': self.state.name }

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
    id = models.AutoField(primary_key=True)
    crash = models.ForeignKey(CrashDumpModel, on_delete=models.CASCADE)
    name = models.CharField('Name', max_length=256, help_text='name of the attachment')
    description = models.TextField('Description', max_length=8192, help_text='description of the attachment')
    storageFile = models.CharField('Storage file', max_length=256, help_text='path to the stored attachment file')

    class Meta:
        verbose_name = "Crash attachment"
        verbose_name_plural = "Crash attachments"

class CrashDumpLink(models.Model):
    id = models.AutoField(primary_key=True)
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
