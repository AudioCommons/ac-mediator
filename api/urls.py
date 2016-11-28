from django.conf.urls import include, url
from api import views

urlpatterns = [
    url(r'^v1/services/$', views.services, name='api-services'),
    url(r'^v1/collect/$', views.collect_response, name='api-collect'),
    url(r'^v1/search/text/$', views.text_search, name='api-text-search'),
    url(r'^v1/license/$', views.licensing, name='api-licensing'),

    # Oauth2 urls
    url(r'^o/', include('api.oauth2_urls', namespace='oauth2_provider')),
]
