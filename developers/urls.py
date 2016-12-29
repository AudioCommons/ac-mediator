from django.conf.urls import url
from developers import views as dev_views

urlpatterns = [
    url(r'^clients/$', dev_views.ApplicationList.as_view(),
        name="developers-app-list"),
    url(r'^clients/register/$', dev_views.ApplicationRegistration.as_view(),
        name="developers-app-register"),
    url(r'^clients/(?P<pk>\d+)/$', dev_views.ApplicationDetail.as_view(),
        name="developers-app-detail"),
    url(r'^clients/(?P<pk>\d+)/delete/$', dev_views.ApplicationDelete.as_view(),
        name="developers-app-delete"),
    url(r'^clients/(?P<pk>\d+)/update/$', dev_views.ApplicationUpdate.as_view(),
        name="developers-app-update"),
    url(r'^clients/(?P<pk>\d+)/monitor/$', dev_views.application_monitor,
        name="developers-app-monitor"),
]
