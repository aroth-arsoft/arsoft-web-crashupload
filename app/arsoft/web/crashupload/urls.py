from django.conf.urls import include
from django.urls import re_path, path
from django.conf import settings
from django.contrib import admin
from arsoft.web.utils import django_debug_urls, django_debug_404, django_debug_500
from django.conf.urls import handler404, handler500, handler403, handler400
from django.contrib.auth import views as auth_views


from .views import CrashDumpListView, CrashDumpDetails, CrashDumpDetailsFromCrashId, \
    CrashDumpDetailsSub, CrashDumpSysInfo, CrashDumpReport, crashdump_new_link, \
        submit, submit_capabilities, submit_crashlist, \
            crashdump_version, nav_items_context
from .migrate import migrate

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    re_path(r'^$', CrashDumpListView.as_view(), name='home'),
    re_path(r'^list/application/(?P<application>[\w\-]+)$', CrashDumpListView.as_view(), name='list_filter_app'),
    re_path(r'^list/application/(?P<application>[\w\-]+)/(?P<state>[\w\-]+)$', CrashDumpListView.as_view(), name='list_filter_app_and_state'),
    re_path(r'^list/state/(?P<state>[\w\-]+)$', CrashDumpListView.as_view(), name='list_filter_state'),
    re_path(r'^view/(?P<pk>\d+)$', CrashDumpDetails.as_view(), name='crash_details'),
    re_path(r'^view/(?P<pk>\d+)/newlink$', crashdump_new_link, name='crash_new_link'),
    re_path(r'^view/(?P<pk>\d+)/view/(?P<page>\w+)$', CrashDumpDetailsSub.as_view(), name='crash_details_view'),
    re_path(r'^view/(?P<pk>\d+)/view/(?P<page>\w+)/(?P<param>[0-9a-fA-F]+)$', CrashDumpDetailsSub.as_view(), name='crash_details_view_sub'),
    re_path(r'^view/(?P<crashid>\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b)$', CrashDumpDetailsFromCrashId.as_view(), name='crash_details_crashid'),
    
    re_path(r'^sysinfo/(?P<pk>\d+)/?(?P<page>\w+)?$', CrashDumpSysInfo.as_view(), name='sysinfo_report'),
    re_path(r'^version$', crashdump_version, name='version'),
    
    #re_path(r'^report/(?P<pk>\d+)/(?P<report_type>\w+)(/(?P<flag>\w+)?)$', CrashDumpReport.as_view(), name='crash_report'),
    re_path(r'^report/(?P<pk>\d+)/(?P<report_type>\w+)/(?P<flag>\w+)$', CrashDumpReport.as_view(), name='crash_report'),
    re_path(r'^submit$', submit, name='submit'),
    re_path(r'^submit/crashlist$', submit_crashlist, name='submit_crashlist'),
    re_path(r'^submit/capabilities$', submit_capabilities, name='submit_capabilities'),
    # easy migrate access to testing
    re_path(r'^migrate$', migrate, name='migrate'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # re_path(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #re_path(r'^admin/', include('admin.site.urls')),

    # Uncomment the next line to enable the admin:
    re_path(r'^debug/', django_debug_urls()),
    re_path(r'^admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html', extra_context=nav_items_context()) ),
    path('accounts/logout/', auth_views.LogoutView.as_view(extra_context=nav_items_context()) ),
    path('oidc/', include('mozilla_django_oidc.urls')),
]

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# ... the rest of your URLconf goes here ...

urlpatterns += staticfiles_urlpatterns("/static")

handler404 = django_debug_404
handler500 = django_debug_500
