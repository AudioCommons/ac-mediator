from django.urls import re_path, include
from api import views

app_name = 'api'
urlpatterns = [
    re_path(r'^v1/services/$', views.services, name='services'),
    re_path(r'^v1/collect/$', views.collect_response, name='collect'),
    re_path(r'^v1/search/text/$', views.text_search, name='text-search'),
    re_path(r'^v1/license/$', views.licensing, name='licensing'),
    re_path(r'^v1/download/$', views.download, name='download'),
    re_path(r'^v1/me/$', views.me, name='me'),

    # Oauth2 urls
    re_path(r'^o/', include('api.oauth2_urls')),

    # Invalid url
    re_path(r'$', views.invalid_url),
]
