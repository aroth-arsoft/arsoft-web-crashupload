from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse

def home(request):

    title = 'Upload crash dump'

    t = loader.get_template('home.html')
    c = RequestContext( request, { 
        'errormessage':error_message, 
        'statusmessage':status_message,
        'username':username,
        'title':title
        })
    return HttpResponse(t.render(c))

def submit(request):
    try:
        filename = request.POST['filename']
        filedata = request.POST['filedata']
    except KeyError:
        error_message = 'Insufficient data.'
        pass

    return HttpResponse("Upload of %s successful." % filename, content_type="text/plain")
