from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from arsoft.web.utils import django_debug_urls

from .views import CrashDumpListView, CrashDumpDetails, CrashDumpDetailsSub, CrashDumpSysInfo, CrashDumpReport, submit
from .migrate import migrate

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    url(r'^$', CrashDumpListView.as_view(), name='home'),
    url(r'^list/application/(?P<application>[\w\-]+)$', CrashDumpListView.as_view(), name='list_filter_app'),
    url(r'^list/application/(?P<application>[\w\-]+)/(?P<state>[\w\-]+)$', CrashDumpListView.as_view(), name='list_filter_app_and_state'),
    url(r'^list/state/(?P<state>[\w\-]+)$', CrashDumpListView.as_view(), name='list_filter_state'),
    url(r'^view/(?P<pk>\d+)$', CrashDumpDetails.as_view(), name='crash_details'),
    url(r'^view/(?P<pk>\d+)/view/(?P<page>\w+)$', CrashDumpDetailsSub.as_view(), name='crash_details_view'),
    url(r'^view/(?P<pk>\d+)/view/(?P<page>\w+)/(?P<param>[0-9a-fA-F]+)$', CrashDumpDetailsSub.as_view(), name='crash_details_view_sub'),
    url(r'^sysinfo/(?P<pk>\d+)/?(?P<page>\w+)?$', CrashDumpSysInfo.as_view(), name='sysinfo_report'),
    
    #url(r'^report/(?P<pk>\d+)/(?P<report_type>\w+)(/(?P<flag>\w+)?)$', CrashDumpReport.as_view(), name='crash_report'),
    url(r'^report/(?P<pk>\d+)/(?P<report_type>\w+)/(?P<flag>\w+)$', CrashDumpReport.as_view(), name='crash_report'),
    url(r'^submit$', submit, name='submit'),
    url(r'^migrate$', migrate, name='migrate'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include('admin.site.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^debug/', include(django_debug_urls())),
]
