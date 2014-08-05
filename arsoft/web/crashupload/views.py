from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from .forms import UploadFileForm
from django.conf import settings
import os.path

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
            print ('dupliacted upload of %s' % file.name)
            item_path = default_storage.path(item_name)
        else:
            item_path = default_storage.save(item_name, ContentFile(file.read()))
        ret = True
    return ret

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
        useragent = request.META['HTTP_USER_AGENT'] if 'HTTP_USER_AGENT' in request.META else None
        if useragent:
            is_terra3d_crashuploader = True if 'terra3d-crashuploader' in useragent else False
        else:
            is_terra3d_crashuploader = False
        remote_addr = _get_remote_addr(request)

        applicationfile = request.POST['applicationfile'] if 'applicationfile' in request.POST else None
        crashid = request.POST['id'] if 'id' in request.POST else None
        timestamp = request.POST['timestamp'] if 'timestamp' in request.POST else None

        minidumpfile = request.FILES['minidump'] if 'minidump' in request.FILES else None
        minidumpreportfile = request.FILES['minidumpreport'] if 'minidumpreport' in request.FILES else None
        coredumpfile = request.FILES['coredump'] if 'coredump' in request.FILES else None
        coredumpreportfile = request.FILES['coredumpreport'] if 'coredumpreport' in request.FILES else None

        result = False
        if _store_dump_file(minidumpfile):
            result = True
        if _store_dump_file(minidumpreportfile):
            result = True
        if _store_dump_file(coredumpfile):
            result = True
        if _store_dump_file(coredumpreportfile):
            result = True

        if is_terra3d_crashuploader:
            if result:
                body = "Upload of crash %s (%s, %s) from %s successful" % (crashid, applicationfile, timestamp, remote_addr)
            else:
                body = "Upload of crash %s (%s, %s) from %s failed" % (crashid, applicationfile, timestamp, remote_addr)
            return HttpResponse(body, content_type="text/plain")
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
