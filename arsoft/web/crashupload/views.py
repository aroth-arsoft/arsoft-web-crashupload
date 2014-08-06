from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django import forms
from .forms import UploadFileForm
from django.conf import settings
import os.path
import logging
from .models import CrashDumpModel



logger = logging.getLogger('arsoft.web.crashupload')

class CrashDumpModelViewForm(forms.ModelForm):
    class Meta:
        model = CrashDumpModel

class CrashDumpListView(ListView):
    model = CrashDumpModel
    template_name = 'crashdumpmodel_list.html'

class CrashDumpDetails(UpdateView):
    model = CrashDumpModel
    template_name = 'crashdumpmodel_update.html'

class CrashDumpReport(UpdateView):
    model = CrashDumpModel
    template_name = 'crashdumpmodel_report.html'

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

def _store_dump_file(file):
    ret = False
    if file:
        item_name = 'dumpdata/' + file.name
        if default_storage.exists(item_name):
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

        applicationfile = request.POST.get('applicationfile')
        crashid = request.POST.get('id')
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

        minidumpfile = request.FILES.get('minidump')
        minidumpreportfile = request.FILES.get('minidumpreport')
        coredumpfile = request.FILES.get('coredump')
        coredumpreportfile = request.FILES.get('coredumpreport')

        db_entry, created = CrashDumpModel.objects.get_or_create(crashid=crashid)

        result = False
        ok, db_entry.minidumpFile = _store_dump_file(minidumpfile)
        if ok:
            result = True
        ok, db_entry.minidumpReportFile = _store_dump_file(minidumpreportfile)
        if ok:
            result = True
        ok, db_entry.coredumpFile = _store_dump_file(coredumpfile)
        if ok:
            result = True
        ok, db_entry.coredumpReportFile = _store_dump_file(coredumpreportfile)
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
