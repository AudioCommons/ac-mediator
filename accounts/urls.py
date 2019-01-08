from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from accounts import views
from oauth2_provider.views.token import AuthorizedTokenDeleteView, AuthorizedTokensListView
from accounts.views import home


# Auth urls
# https://stackoverflow.com/questions/6930982/how-to-use-a-variable-inside-a-regular-expression
domainPrefix = "authenticate/"
# domainPrefix = ""
urlpatterns = [
    # Home
    url(r'^%s$' % domainPrefix, home, name='home'),
    url(r'^%sabout/$' % domainPrefix, views.about, name='about'),

    # Link services
    url(r'^%slink_services/$' % domainPrefix, views.link_services, name='link_services'),
    url(r'^%slink_service/(?P<service_id>[^\/]+)/$' % domainPrefix, views.link_service_callback, name='link_service_callback'),
    url(r'^%slink_service_get_token/(?P<service_id>[^\/]+)/$' % domainPrefix, views.link_service_get_token, name='link_service_get_token'),
    url(r'^%sunlink_service/(?P<service_id>[^\/]+)/$' % domainPrefix, views.unlink_service, name='unlink_service'),

    # Manage given api credentials
    url(r'^%sauthorized_clients/$' % domainPrefix, AuthorizedTokensListView.as_view(
        template_name='accounts/authorized-tokens.html',
    ), name="authorized-token-list"),
    url(r'^%sauthorized_clients/(?P<pk>\d+)/delete/$' % domainPrefix, AuthorizedTokenDeleteView.as_view(
        template_name='accounts/authorized-token-delete.html',
        success_url=reverse_lazy('authorized-token-list'),
    ), name="authorized-token-delete"),
]
