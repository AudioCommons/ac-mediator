from django.conf.urls import include, url
from api import views

urlpatterns = [
    url(r'^services/$', views.services, name='api-services'),
    url(r'^collect/$', views.collect_response, name='api-collect'),
    url(r'^search/text/$', views.text_search, name='api-text-search'),
    url(r'^license/$', views.licensing, name='api-licensing'),

    # Oauth2 urls
    url(r'^o/', include('api.oauth2_urls', namespace='oauth2_provider')),
]
