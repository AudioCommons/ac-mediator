from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from accounts import views
from oauth2_provider.views.token import AuthorizedTokenDeleteView, AuthorizedTokensListView
from accounts.views import home


urlpatterns = [
    # Home
    url(r'^$', home, name='home'),

    # Link services
    url(r'^link_services/$', views.link_services, name='link_services'),
    url(r'^link_service/(?P<service_id>[^\/]+)/$', views.link_service_callback, name='link_service_callback'),
    url(r'^link_service_get_token/(?P<service_id>[^\/]+)/$', views.link_service_get_token, name='link_service_get_token'),
    url(r'^unlink_service/(?P<service_id>[^\/]+)/$', views.unlink_service, name='unlink_service'),

    # Manage given api credentials
    url(r'^authorized_clients/$', AuthorizedTokensListView.as_view(
        template_name='accounts/authorized-tokens.html',
    ), name="authorized-token-list"),
    url(r'^authorized_clients/(?P<pk>\d+)/delete/$', AuthorizedTokenDeleteView.as_view(
        template_name='accounts/authorized-token-delete.html',
        success_url=reverse_lazy('authorized-token-list'),
    ), name="authorized-token-delete"),
]
