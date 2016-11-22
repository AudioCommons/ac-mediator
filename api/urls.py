from django.conf.urls import include, url
from api import views

urlpatterns = [
    url(r'^services/$', views.services),
    url(r'^collect/$', views.collect_response),
    url(r'^search/text/$', views.text_search),
    url(r'^license/$', views.licensing),

    # Oauth2 urls
    url(r'^o/', include('api.oauth2_urls', namespace='oauth2_provider')),
]
