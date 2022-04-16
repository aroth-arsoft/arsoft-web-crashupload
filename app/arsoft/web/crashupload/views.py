from random import choices
from urllib import request
from django.template import RequestContext, loader
from django.urls import reverse
from django.core import serializers
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseNotAllowed, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.base import RedirectView
from django import forms
from django_tables2.views import SingleTableView, SingleTableMixin
from django_filters.views import FilterView
import django_filters
from django.conf import settings

import os.path
from io import StringIO
import logging
import time
from .models import CrashDumpProject, CrashDumpSetting, CrashDumpState, CrashDumpModel, CrashDumpLink, CrashDumpAttachment
from .tables import CrashDumpModelTable
from .forms import UploadFileForm
from uuid import UUID
from django.conf import settings as django_settings

from crashdump.utils import *
from crashdump.minidump import MiniDump
from crashdump.xmlreport import XMLReport
from crashdump.systeminforeport import SystemInfoReport

from arsoft.web.crashupload.gitlab import gitlab_create_issue, gitlab_get_issue

logger = logging.getLogger('arsoft.web.crashupload')

# 16 MB
DEFAULT_MAX_UPLOAD_SIZE = 16 * 1024 * 1024

def safe_get_as_int (l, default=None):
    try:
        return int(l)
    except ValueError:
        return default

def add_utils_to_context(context, crash=None):

    context['nav_items'] = django_settings.NAV_ITEMS
    context['hex_format'] = hex_format
    context['exception_code'] = exception_code
    context['format_bool_yesno'] = format_bool_yesno
    context['format_source_line'] = format_source_line
    context['format_function_plus_offset'] = format_function_plus_offset
    context['str_or_unknown'] = str_or_unknown
    context['format_cpu_type'] = format_cpu_type
    context['format_cpu_vendor'] = format_cpu_vendor
    context['format_cpu_name'] = format_cpu_name
    context['format_platform_type'] = format_platform_type
    context['format_os_version'] = format_os_version
    context['format_distribution_id'] = format_distribution_id
    context['format_distribution_codename'] = format_distribution_codename
    context['format_milliseconds'] = format_milliseconds
    context['format_seconds'] = format_seconds
    context['format_size'] = format_size
    context['format_trust_level'] = format_trust_level
    context['format_memory_usagetype'] = format_memory_usagetype
    context['format_gl_extension_name'] = format_gl_extension_name
    context['format_version_number'] = format_version_number
    context['format_thread'] = format_thread
    context['thread_extra_info'] = thread_extra_info
    context['format_stack_frame'] = format_stack_frame
    if crash is None:
        context['addr_format'] = addr_format
    else:
        context['addr_format'] = addr_format_64 if crash.is_64_bit else addr_format_32
        context['is_64_bit'] = crash.is_64_bit
        context['bits'] = 64 if crash.is_64_bit else 32

        xmlfile = None
        xmlfile_from_db = None
        minidumpfile = None
        coredumpfile = None
        if crash.has_minidump:
            xmlfile_from_db = crash.minidumpReportXMLFile
            xmlfile = _get_dump_filename(crash, crash.minidumpReportXMLFile)
            minidumpfile = _get_dump_filename(crash, crash.minidumpFile)
        elif crash.has_coredump:
            xmlfile_from_db = crash.coredumpReportXMLFile
            xmlfile = _get_dump_filename(crash, crash.coredumpReportXMLFile)
            coredumpfile = _get_dump_filename(crash, crash.coredumpFile)
        context['xmlfile_from_db'] = xmlfile_from_db
        context['xmlfile'] = xmlfile
        context['xmlfile_error'] = None
        context['minidumpfile_error'] = None
        context['minidump_xml_size'] = 0
        context['coredump_xml_size'] = 0
        context['minidumpfile_size'] = 0
        context['coredumpfile_size'] = 0
        context['xmlfile_size'] = 0
        context['reporttextfile_size'] = 0
        context['reporthtmlfile_size'] = 0
        context['show_debug_info'] = True
        context['parsetime'] = 0
        context['dbtime'] = 0

        for f in XMLReport._main_fields:
            context[f] = None

        if xmlfile:
            start = time.time()
            if minidumpfile:
                try:
                    context['minidumpfile_size'] = os.path.getsize(minidumpfile)
                    context['minidumpfile'] = MiniDump(minidumpfile)
                except (OSError, AssertionError) as e:
                    context['minidumpfile_error'] = str(e)
                    pass
            else:
                context['minidumpfile_error'] = "No minidump file available"
            if coredumpfile:
                try:
                    context['coredumpfile_size'] = os.path.getsize(coredumpfile)
                except OSError:
                    pass
            if os.path.isfile(xmlfile):
                try:
                    xmlreport = XMLReport(xmlfile)
                    for f in xmlreport.fields:
                        context[f] = XMLReport.ProxyObject(xmlreport, f)
                    context['xmlreport'] = xmlreport
                    context['is_64_bit'] = xmlreport.is_64_bit
                except XMLReport.XMLReportIOError as e:
                    context['xmlfile_error'] = str(e)
            else:
                wrapper = MiniDumpWrapper(context['minidumpfile'])
                for f in wrapper.fields:
                    context[f] = MiniDumpWrapper.ProxyObject(wrapper, f)
                context['xmlreport'] = None
                context['xmlfile_error'] = 'XML file %s does not exist' % xmlfile
            end = time.time()
            context['parsetime'] = end - start
        else:
            xmlfile_error = 'No XML file available'
        context['bits'] = 64 if context['is_64_bit'] else 32
        context['addr_format'] = addr_format_64 if context['is_64_bit'] else addr_format_32    

class CrashDumpModelViewForm(forms.ModelForm):
    class Meta:
        model = CrashDumpModel
        fields = '__all__'


class CrashDumpFilter(django_filters.FilterSet):
    #state = django_filters.ModelChoiceFilter(queryset=CrashDumpState.objects.all())
    #state = django_filters.ModelChoiceFilter(queryset=CrashDumpState.objects.values_list('id', 'name'))
    applicationName = django_filters.CharFilter(lookup_expr='iexact')
    reportHostName = django_filters.CharFilter(lookup_expr='iexact')
    reportUserName = django_filters.CharFilter(lookup_expr='iexact')
    crashHostName = django_filters.CharFilter(lookup_expr='iexact')
    crashUserName = django_filters.CharFilter(lookup_expr='iexact')
    buildType = django_filters.ChoiceFilter(choices=CrashDumpModel.BUILDTYPES)

    class Meta:
        model = CrashDumpModel
        fields = [
            'state',
            'applicationName', 
            'reportHostName', 'reportUserName',
            'crashHostName', 'crashUserName',
            'buildType','productTargetVersion'
            ]

    def __init__(self, *args, **kwargs):
        super(CrashDumpFilter, self).__init__(*args, **kwargs)
        # You need to override the label_from_instance method in the filter's form field
        self.filters['state'].field.label_from_instance = lambda obj: obj.name


class CrashDumpListView(SingleTableMixin, FilterView):
    model = CrashDumpModel
    table_class = CrashDumpModelTable
    template_name = 'list.html'
    application = None
    state = None

    filterset_class = CrashDumpFilter

    def dispatch(self, request, *args, **kwargs):
        if 'application' in kwargs:
            self.application = kwargs['application']
        if 'state' in kwargs:
            self.state = kwargs['state']
        context = super(CrashDumpListView, self).dispatch(request, *args, **kwargs)
        return context

    def get_context_data(self, **kwargs):
        context = super(CrashDumpListView, self).get_context_data(**kwargs)
        if 'application' in self.kwargs:
            context['application'] = self.kwargs['application']
        if 'state' in self.kwargs:
            context['state'] = self.kwargs['state']
        add_utils_to_context(context)
        return context

    # def get_queryset(self):
    #     if self.application and self.state:
    #         return self.model.objects.filter(applicationName=self.application, state=CrashDumpState.objects.get(name=self.state))
    #     elif self.application:
    #         return self.model.objects.filter(applicationName=self.application)
    #     elif self.state:
    #         return self.model.objects.filter(state=CrashDumpState.objects.get(name=self.state))
    #     else:
    #         return super(CrashDumpListView, self).get_queryset()

class CrashDumpDetails(DetailView):
    model = CrashDumpModel
    template_name = 'report.html'

    def get_context_data(self, **kwargs):
        start = time.time()

        context = super(CrashDumpDetails, self).get_context_data(**kwargs)
        try:
            links = CrashDumpLink.objects.filter(crash=self.object.id)
        except CrashDumpLink.DoesNotExist:
            links = None
        try:
            attachments = CrashDumpAttachment.objects.filter(crash=self.object.id)
        except CrashDumpAttachment.DoesNotExist:
            attachments = None
        error = self.request.GET.get('error')
        if error:
            context['error'] = error

        project = CrashDumpProject.findByCodename(self.object.productCodeName)

        context['project'] = project
        context['links'] = links
        context['attachments'] = attachments
        add_utils_to_context(context, crash=self.object)
        end = time.time()
        context['dbtime'] = end - start
        return context


def patch_url(url, params=None):
    from urllib.parse import urlencode, parse_qsl, urlparse, urlunparse
    url_parts = list(urlparse(url))
    query = dict(parse_qsl(url_parts[4]))
    if params is not None:
        query.update(params)
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)

def crash_to_issue(request, obj, issue=None):
    error = None
    proj = None
    if obj is not None:
        if obj.productCodeName:
            proj = CrashDumpProject.findByCodename(obj.productCodeName)
            if proj is None:
                error = 'No project matching codename %s' % obj.productCodeName
        else:
            error = 'No codename available for crash %s' % obj.id
    else:
        error = 'Unable to find crash %s' % obj.id
    if proj:
        crash_url = request.build_absolute_uri(obj.url)

        default_description = """The crash [{crash.uuid}]({crash_url}) has been uploaded by **{crash.reportUserName}**
from **{crash.reportHostName}** and linked to this ticket.

The crash occured at {crash.crashtimestamp} on **{crash.crashHostName}** with user **{crash.crashUserName}** while running `{crash.applicationName}`. The
application was running as part of {crash.productName} ({crash.productCodeName}) version {crash.productVersion} ({crash.productTargetVersion}, {crash.buildType}) on a
{crash.systemName}/{crash.machineType} with {crash.osVersion} ({crash.osRelease}/{crash.osMachine}).
"""

        info = {'crash': obj, 'crash_url': crash_url, 'project': proj }
        title = CrashDumpSetting.get('issue_title', 'Crash {crash.uuid}')
        description = CrashDumpSetting.get('issue_description', default_description)
        labels = []
        for l in CrashDumpSetting.get('issue_labels', 'crash').split(','):
            labels.append(l.format(**info))
        
        title = title.format(**info)
        description = description.format(**info)
        if issue is None:
            issue = {}
        issue['title'] = title
        issue['description'] = description
        issue['labels'] = labels
    else:
        issue = None
    return issue, proj, error

def crash_get_or_create_issue_link(request, obj, issue):
    link_obj = None
    error = None
    proj = None
    issue, proj, error = crash_to_issue(request, obj, issue)
    if proj:
        if proj.issueTrackerType == CrashDumpProject.GITLAB:
            existing_issue, error = gitlab_get_issue(url=proj.issueTrackerUrl, token=proj.issueTrackerToken, issue=issue)
            if not existing_issue:
                existing_issue, error = gitlab_create_issue(url=proj.issueTrackerUrl, token=proj.issueTrackerToken, issue=issue)

            if existing_issue and not error:
                existing_links = CrashDumpLink.objects.filter(crash=obj, url=existing_issue.get('web_url'))
                if not existing_links:
                    link_obj = CrashDumpLink.objects.create(crash=obj, name='Issue %s' % existing_issue.get('iid'), url=existing_issue.get('web_url'))        
                    if link_obj:
                        link_obj.save()
                else:
                    link_obj = existing_links[0]
    return link_obj, error


def crashdump_new_link(request, *args, **kwargs):
    if request.method == 'POST':
        error = None
        obj = get_object_or_404(CrashDumpModel, id=kwargs['pk'])
                    
        link_obj, error = crash_get_or_create_issue_link(request, obj)

        redir_url = reverse('crash_details', args=[obj.id])
        if error:
            redir_url = patch_url(redir_url, {'error': error})

        return HttpResponseRedirect(redir_url)
    else:
        body = "No crash dump data provided."
        return HttpResponse(body, status=400, content_type="text/plain")


class CrashDumpDetailsFromCrashId(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(CrashDumpModel, crashid=kwargs['crashid'])
        return reverse('crash_details', args=[obj.id] )

class CrashDumpDetailsSub(DetailView):
    model = CrashDumpModel
    template_name = None

    def setup(self, request, *args, **kwargs):
        super(CrashDumpDetailsSub, self).setup(request, *args, **kwargs)
        page = kwargs.get('page')
        if page is None:
            raise Http404("Page not found")
        self.page = page
        self.param = kwargs.get('param')
        self.template_name = '%s.html' % self.page

    def get_context_data(self, **kwargs):
        context = super(CrashDumpDetailsSub, self).get_context_data(**kwargs)
        add_utils_to_context(context, crash=self.object)
        if self.page in ['sysinfo', 'sysinfo_ex',
                            'fast_protect_version_info', 'exception', 'memory_blocks', 'memory_regions', 'modules', 'threads', 'stackdumps',
                            'file_info' ]:
            pass
        elif self.page == 'memory_block':
            block_base = safe_get_as_int(self.param, 0)
            memory_block = None
            for b in context['memory_blocks']:
                if b.base == block_base:
                    memory_block = b
                    break
            memory = memory_block.memory if memory_block is not None else None
            hexdump = memory.hexdump if memory is not None else None
            context.update({'memory_block': memory_block, 'memory': memory, 'hexdump': hexdump, 'memory_block_base': block_base })
        elif self.page == 'stackdump':
            threadid = safe_get_as_int(self.param, 0)
            stackdump = None
            if threadid in context['stackdumps']:
                stackdump = context['stackdumps'][threadid]
            context.update({'stackdump': stackdump, 'threadid': threadid })

        return context

class CrashDumpSysInfo(DetailView):
    model = CrashDumpModel
    template_name = 'sysinfo_report.html'

    def setup(self, request, *args, **kwargs):
        super(CrashDumpSysInfo, self).setup(request, *args, **kwargs)
        page = kwargs.get('page')
        self.page = page
        self.param = kwargs.get('param')
        if self.page:
            self.template_name = '%s.html' % self.page

    def get_context_data(self, **kwargs):
        start = time.time()
        context = super(CrashDumpSysInfo, self).get_context_data(**kwargs)
        add_utils_to_context(context, crash=self.object)
        if 'xmlreport' in context:
            xmlfile = context['xmlreport']
            context['sysinfo_report'] = None
            if isinstance(xmlfile, XMLReport) or (isinstance(xmlfile, string) and os.path.isfile(xmlfile)):
                try:
                    context['sysinfo_report'] = SystemInfoReport(xmlreport=xmlfile)
                except SystemInfoReport.SystemInfoReportException as e:
                    context['xmlfile_error'] = str(e)
            else:
                context['xmlfile_error'] = _("XML file %(file)s is unavailable", file=xmlfile)

        end = time.time()
        context['dbtime'] = end - start
        return context

class CrashDumpReport(DetailView):
    model = CrashDumpModel
    template_name = 'crashdumpmodel_report.html'

    def get_context_data(self, **kwargs):
        context = super(CrashDumpReport, self).get_context_data(**kwargs)
        if 'report_type' in self.kwargs:
            context['report_type'] = self.kwargs['report_type']
        if 'flag' in self.kwargs:
            context['flag'] = self.kwargs['flag']
        add_utils_to_context(context)
        return context

    def render_to_response(self, context, **response_kwargs):
        filename = None
        if context['report_type'] == 'minidumpTextReport':
            filename = self.object.minidumpReportTextFile
        elif context['report_type'] == 'minidumpXMLReport':
            filename = self.object.minidumpReportXMLFile
        elif context['report_type'] == 'minidumpHTMLReport':
            filename = self.object.minidumpReportHTMLFile
        elif context['report_type'] == 'minidump':
            filename = self.object.minidumpFile
        elif context['report_type'] == 'coredumpTextReport':
            filename = self.object.coredumpReportTextFile
        elif context['report_type'] == 'coredumpXMLReport':
            filename = self.object.coredumpReportXMLFile
        elif context['report_type'] == 'coredumpHTMLReport':
            filename = self.object.coredumpReportHTMLFile
        elif context['report_type'] == 'coredump':
            filename = self.object.coredumpFile
        elif context['report_type'] == 'gfxCaps':
            filename = self.object.gfxCapsFile

        if context['flag'] == 'raw':
            if filename is None:
                response = HttpResponse('File not found', status=404, content_type="text/plain")
            else:
                item_path = None
                item_name = os.path.basename(filename)
                if default_storage.exists(filename):
                    item_path = default_storage.path(filename)

                if item_path:
                    body = open(item_path, "rb").read()
                    response = HttpResponse(body, content_type='application/force-download')
                    response['Content-Disposition'] = 'attachment; filename=%s' % item_name
                else:
                    response = HttpResponse('File not found', status=404, content_type="text/plain")
            return response
        elif context['flag'] == 'text':
            if filename is None:
                return HttpResponse('File not found', status=404, content_type="text/plain")
            else:
                item_path = None
                item_name = os.path.basename(filename)
                if default_storage.exists(filename):
                    item_path = default_storage.path(filename)

                if item_path:
                    context['content'] = open(item_path, "rb").read()
            return super(CrashDumpReport, self).render_to_response(context, **response_kwargs)
        elif context['flag'] == 'html':
            if filename is None:
                return HttpResponse('File not found', status=404, content_type="text/plain")
            else:
                item_path = None
                item_name = os.path.basename(filename)
                if default_storage.exists(filename):
                    item_path = default_storage.path(filename)

                if item_path:
                    xmlreport = XMLReport(item_path)
                    for f in xmlreport.fields:
                        context[f] = getattr(xmlreport, f)
                    context['content'] = str(xmlreport.fields)
            return super(CrashDumpReport, self).render_to_response(context, **response_kwargs)
        else:
            return super(CrashDumpReport, self).render_to_response(context, **response_kwargs)

def home(request):
    title = 'Upload crash dump'
    try:
        filename = request.session['filename']
        result = request.session['result']
        if result:
            status_message = request.session['error_message']
            error_message = ''
        else:
            error_message = request.session['error_message']
            status_message = ''
    except (KeyError):
        error_message = ''
        status_message = ''
        filename = ''
        pass

    if request.method == 'POST':
        title = 'post'
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/success/url/')
    else:
        form = UploadFileForm()
    t = loader.get_template('home.html')
    c = RequestContext( request, {
        'errormessage':error_message,
        'statusmessage':status_message,
        'filename':filename,
        'title':title,
        'form': form
        })
    return HttpResponse(t.render(c))

def _store_dump_file(crashid, request, name):
    ret = False
    file = request.FILES.get(name)
    if file:
        force = bool(request.POST.get('force'))
        item_name = 'dumpdata/%s/%s' % (crashid, file.name)
        if default_storage.exists(item_name):
            if force:
                default_storage.delete(item_name)
                item_path = default_storage.save(item_name, ContentFile(file.read()))
            else:
                item_path = default_storage.path(item_name)
        else:
            item_path = default_storage.save(item_name, ContentFile(file.read()))
        ret = True
    else:
        item_name = None
    return (ret, item_name)

def _get_dump_filename(crashobj, filename):
    if not filename:
        return None
    item_name = 'dumpdata/%s' % (filename)
    if default_storage.exists(item_name):
        return default_storage.path(item_name)
    else:
        return None


def _get_remote_addr(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@csrf_exempt
def submit(request):
    file = None
    error_message = None

    if request.method == 'POST':
        useragent = request.META.get('HTTP_USER_AGENT')
        if useragent:
            is_terra3d_crashuploader = True if 'terra3d-crashuploader' in useragent else False
        else:
            is_terra3d_crashuploader = False
        remote_addr = _get_remote_addr(request)
        links = None

        id_str = request.POST.get('id')
        if id_str and id_str != '00000000-0000-0000-0000-000000000000' and id_str != '{00000000-0000-0000-0000-000000000000}':
            crashid = UUID(id_str)
            result = True
        else:
            result = False
        if result:
            applicationfile = request.POST.get('applicationfile')
            applicationname = request.POST.get('applicationname')
            force = request.POST.get('force')
            crashtimestamp = request.POST.get('crashtimestamp')
            reporttimestamp = request.POST.get('reporttimestamp')

            productname = request.POST.get('productname')
            productcodename = request.POST.get('productcodename')
            productversion = request.POST.get('productversion')
            producttargetversion = request.POST.get('producttargetversion')
            fqdn = request.POST.get('fqdn')
            username = request.POST.get('username')
            crashfqdn = request.POST.get('crashfqdn')
            crashusername = request.POST.get('crashusername')
            buildtype = request.POST.get('buildtype')
            buildpostfix = request.POST.get('buildpostfix')
            machinetype = request.POST.get('machinetype')
            cputype = safe_get_as_int(request.POST.get('cputype'), -1)
            systemname = request.POST.get('systemname')
            osversion = request.POST.get('osversion')
            osrelease = request.POST.get('osrelease')
            osmachine = request.POST.get('osmachine')
            sysinfo = request.POST.get('sysinfo')

            ticket_str = request.POST.get('ticket') or 'no'

            db_entry, created = CrashDumpModel.objects.get_or_create(crashid=crashid, 
                                        defaults={'state': CrashDumpState.objects.get(name='new') })
            if not created and not force:
                result = False
            else:
                result = False
                ok, db_entry.minidumpFile = _store_dump_file(crashid, request, 'minidump')
                if ok:
                    result = True
                ok, db_entry.minidumpReportTextFile = _store_dump_file(crashid, request, 'minidumpreport')
                if ok:
                    result = True
                ok, db_entry.minidumpReportXMLFile = _store_dump_file(crashid, request, 'minidumpreportxml')
                if ok:
                    result = True
                ok, db_entry.minidumpReportHTMLFile = _store_dump_file(crashid, request, 'minidumpreporthtml')
                if ok:
                    result = True
                ok, db_entry.coredumpFile = _store_dump_file(crashid, request, 'coredump')
                if ok:
                    result = True
                ok, db_entry.coredumpReportTextFile = _store_dump_file(crashid, request, 'coredumpreport')
                if ok:
                    result = True
                ok, db_entry.coredumpReportXMLFile = _store_dump_file(crashid, request, 'coredumpreportxml')
                if ok:
                    result = True
                ok, db_entry.coredumpReportHTMLFile = _store_dump_file(crashid, request, 'coredumpreporthtml')
                if ok:
                    result = True
                ok, db_entry.gfxCapsFile = _store_dump_file(crashid, request, 'gfxcaps')
                if ok:
                    result = True

        if result:
            try:
                links = CrashDumpLink.objects.filter(crash=db_entry.id)
            except CrashDumpLink.DoesNotExist:
                links = None

            db_entry.crashtimestamp = crashtimestamp
            db_entry.reporttimestamp = reporttimestamp

            db_entry.applicationFile = applicationfile

            # don't trust the applicationname provided by the client
            appbase = os.path.basename(applicationfile)
            (appbase, ext) = os.path.splitext(appbase)
            if buildpostfix and appbase.endswith(buildpostfix):
                appbase = appbase[:-len(buildpostfix)]
            db_entry.applicationName = appbase

            db_entry.productName = productname
            db_entry.productCodeName = productcodename
            db_entry.productVersion = productversion
            db_entry.productTargetVersion = producttargetversion
            db_entry.clientHostName = fqdn
            db_entry.clientUserName = username
            db_entry.crashHostName = crashfqdn
            db_entry.crashUserName = crashusername

            db_entry.buildType = buildtype
            db_entry.buildPostfix = buildpostfix

            db_entry.machineType = machinetype
            db_entry.cpuType = cputype
            db_entry.systemName = systemname
            db_entry.osVersion = osversion
            db_entry.osRelease = osrelease
            db_entry.osMachine = osmachine
            db_entry.systemInfoData = sysinfo
            db_entry.save()

            if ticket_str == 'no':
                pass
            elif '#' in ticket_str:
                if 1:
                    # link to given issue/ticket
                    # link_obj, error = crash_get_or_create_issue_link(request, db_entry)
                    pass
                else:
                    ticket_ids = []
                    for t in ticket_str.split(','):
                        if t[0] == '#':
                            ticket_ids.append(int(t[1:]))
                    ticketobjs = []
                    for tkt_id in ticket_ids:
                        try:
                            ticketobjs.append(Ticket(env=self.env, tkt_id=tkt_id))
                        except ResourceNotFound:
                            return self._error_response(req, status=HTTPNotFound.code, body='Ticket %i not found. Cannot link crash %s to the requested ticket.' % (tkt_id, str(uuid)))

            elif ticket_str == 'auto':
                if not links:
                    link_obj, error = crash_get_or_create_issue_link(request, db_entry)
            elif ticket_str == 'new':
                link_obj, error = crash_get_or_create_issue_link(request, db_entry)


        if is_terra3d_crashuploader:
            headers = {}

            if result:
                crash_url = request.build_absolute_uri(db_entry.url)
                headers['Crash-URL'] = crash_url
                headers['CrashId'] = db_entry.uuid

                linked_ticket_header = []
                for lnk in links:
                    linked_ticket_header.append('#%i:%s' % (lnk.name, lnk.url))
                if linked_ticket_header:
                    headers['Linked-Tickets'] = ';'.join(linked_ticket_header)

                body = "Upload of crash %s (%s, %s) from %s successful" % (crashid, applicationfile, crashtimestamp, remote_addr)
                status_code = 200
            else:
                body = "Upload of crash %s (%s, %s) from %s failed" % (crashid, applicationfile, crashtimestamp, remote_addr)
                status_code = 500
            return HttpResponse(body, status=status_code, headers=headers, content_type="text/plain")
        else:
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            request.session['error_message'] = error_message
            request.session['result'] = result
            return HttpResponseRedirect(reverse('arsoft.web.crashupload.views.home'))
    else:
        body = "No crash dump data provided."
        return HttpResponse(body, status=400, content_type="text/plain")

@csrf_exempt
def submit_crashlist(request):
    if request.method == 'GET':
        data = []
        args = {}
        state = request.GET.get('state')
        if state is not None:
            try:
                state_obj = CrashDumpState.objects.filter(name=state)
                args = {'state': state_obj }
            except CrashDumpState.DoesNotExist:
                raise Http404("CrashDumpState %s does not exist" % state)
        list = CrashDumpModel.objects.filter(**args)
        for obj in list:
            data.append(obj.to_json())
        return JsonResponse({'list': data })
    else:
        return HttpResponseNotAllowed(permitted_methods=['GET'])

def safe_int(s, default_value=None):
    if s:
        try:
            n = int(s)
            return n
        except ValueError:
            return default_value
    else:
        return default_value


@csrf_exempt
def submit_capabilities(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(permitted_methods=['GET'])

    user_agent = request.META.get('HTTP_USER_AGENT')
    if user_agent is None:
        return HttpResponseForbidden('No user-agent specified.')

    max_upload_size = safe_int(CrashDumpSetting.get('max_upload_size', DEFAULT_MAX_UPLOAD_SIZE))
    upload_disabled = safe_int(CrashDumpSetting.get('upload_disabled', False))

    headers = {}
    headers['Max-Upload-Size'] = max_upload_size
    headers['Upload-Disabled'] = '1' if upload_disabled else '0'
    headers['Version'] = '2'
    headers['Crashdump-Plugin-Version'] = '2'

    return JsonResponse(headers, headers=headers)
