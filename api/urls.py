from django.conf.urls import include, url
from api import views

urlpatterns = [
    url(r'^services/$', views.Services.as_view()),
    url(r'^search/$', views.Search.as_view()),

    # Oauth2 urls
    url(r'^o/', include('api.oauth2_urls', namespace='oauth2_provider')),
]
