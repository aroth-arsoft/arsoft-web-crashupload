from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
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


def submit(request):
    file = None
    error_message = None
    try:
        file = request.FILES['file']
    except KeyError:
        error_message = 'No file uploaded.'
        pass

    filedata = None
    if file:
        path = default_storage.save(file.name, ContentFile(file.read()))
        filedata = os.path.join(settings.MEDIA_ROOT, path)
    else:
        result_code = False

    body = "Upload of %s successful. %s files %s" % (str(file), filedata, str(request.FILES))

    return HttpResponse(body, content_type="text/plain")

    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    request.session['filename'] = filename
    request.session['error_message'] = error_message
    request.session['result'] = result_code
    return HttpResponseRedirect(reverse('arsoft.web.crashupload.views.home'))
