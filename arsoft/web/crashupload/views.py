from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView
from django import forms
from .forms import UploadFileForm
from django.conf import settings
import os.path
from StringIO import StringIO
import logging
from .models import CrashDumpState, CrashDumpModel, CrashDumpLink, CrashDumpAttachment
from .xmlreport import XMLReport
from uuid import UUID

logger = logging.getLogger('arsoft.web.crashupload')

class CrashDumpModelViewForm(forms.ModelForm):
    class Meta:
        model = CrashDumpModel
        fields = '__all__'

class CrashDumpListView(ListView):
    model = CrashDumpModel
    template_name = 'crashdumpmodel_list.html'
    application = None
    state = None

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
        return context

    def get_queryset(self):
        if self.application and self.state:
            return self.model.objects.filter(applicationName=self.application, state=CrashDumpState.objects.get(name=self.state))
        elif self.application:
            return self.model.objects.filter(applicationName=self.application)
        elif self.state:
            return self.model.objects.filter(state=CrashDumpState.objects.get(name=self.state))
        else:
            return super(CrashDumpListView, self).get_queryset()

class CrashDumpDetails(DetailView):
    model = CrashDumpModel
    template_name = 'crashdumpmodel_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CrashDumpDetails, self).get_context_data(**kwargs)
        try:
            links = CrashDumpLink.objects.get(crash=self.object.id)
        except CrashDumpLink.DoesNotExist:
            links = None
        try:
            attachments = CrashDumpAttachment.objects.get(crash=self.object.id)
        except CrashDumpAttachment.DoesNotExist:
            attachments = None
        context['links'] = links
        context['attachments'] = attachments
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
                    body = StringIO(file(item_path, "rb").read())
                    response = HttpResponse(body, mimetype='application/force-download')
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
                    context['content'] = file(item_path, "rb").read()
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

        id_str = request.POST.get('id')
        if id_str and id_str != '00000000-0000-0000-0000-000000000000' and id_str != '{00000000-0000-0000-0000-000000000000}':
            crashid = UUID(id_str)
            result = True
        else:
            result = False
        if result:
            applicationfile = request.POST.get('applicationfile')
            force = request.POST.get('force')
            timestamp = request.POST.get('timestamp')

            productname = request.POST.get('productname')
            productversion = request.POST.get('productversion')
            producttargetversion = request.POST.get('producttargetversion')
            fqdn = request.POST.get('fqdn')
            username = request.POST.get('username')
            buildtype = request.POST.get('buildtype')
            buildpostfix = request.POST.get('buildpostfix')
            machinetype = request.POST.get('machinetype')
            systemname = request.POST.get('systemname')
            osversion = request.POST.get('osversion')
            osrelease = request.POST.get('osrelease')
            osmachine = request.POST.get('osmachine')
            sysinfo = request.POST.get('sysinfo')

            db_entry, created = CrashDumpModel.objects.get_or_create(crashid=crashid, defaults={'state': CrashDumpState.objects.get(name='new') })
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
            db_entry.timestamp = timestamp
            db_entry.applicationFile = applicationfile

            appbase = os.path.basename(applicationfile)
            (appbase, ext) = os.path.splitext(appbase)
            if buildpostfix and appbase.endswith(buildpostfix):
                appbase = appbase[:-len(buildpostfix)]
            db_entry.applicationName = appbase

            db_entry.productName = productname
            db_entry.productVersion = productversion
            db_entry.productTargetVersion = producttargetversion
            db_entry.clientHostName = fqdn
            db_entry.clientUserName = username

            db_entry.buildType = buildtype
            db_entry.buildPostfix = buildpostfix

            db_entry.machineType = machinetype
            db_entry.systemName = systemname
            db_entry.osVersion = osversion
            db_entry.osRelease = osrelease
            db_entry.osMachine = osmachine
            db_entry.systemInfoData = sysinfo
            db_entry.save()

        if is_terra3d_crashuploader:
            if result:
                body = "Upload of crash %s (%s, %s) from %s successful" % (crashid, applicationfile, timestamp, remote_addr)
                status_code = 200
            else:
                body = "Upload of crash %s (%s, %s) from %s failed" % (crashid, applicationfile, timestamp, remote_addr)
                status_code = 500
            return HttpResponse(body, status=status_code, content_type="text/plain")
        else:
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            request.session['error_message'] = error_message
            request.session['result'] = result_code
            return HttpResponseRedirect(reverse('arsoft.web.crashupload.views.home'))
    else:
        body = "No crash dump data provided."
        return HttpResponse(body, status=400, content_type="text/plain")
