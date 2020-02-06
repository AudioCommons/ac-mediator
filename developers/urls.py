from django.urls import re_path
from developers import views as dev_views

app_name = 'developers'
urlpatterns = [
    re_path(r'^clients/$', dev_views.ApplicationList.as_view(),
        name="app-list"),
    re_path(r'^clients/register/$', dev_views.ApplicationRegistration.as_view(),
        name="app-register"),
    re_path(r'^clients/(?P<pk>\d+)/$', dev_views.ApplicationDetail.as_view(),
        name="app-detail"),
    re_path(r'^clients/(?P<pk>\d+)/delete/$', dev_views.ApplicationDelete.as_view(),
        name="app-delete"),
    re_path(r'^clients/(?P<pk>\d+)/update/$', dev_views.ApplicationUpdate.as_view(),
        name="app-update"),
    re_path(r'^clients/(?P<pk>\d+)/monitor/$', dev_views.application_monitor,
        name="app-monitor"),
    re_path(r'^clients/(?P<pk>\d+)/monitor/data/$', dev_views.get_application_monitor_data,
        name="app-monitor-data"),
]
