from django.conf.urls import include, url
from api import views

urlpatterns = [
    url(r'^services/$', views.Services.as_view()),
    url(r'^search/text/$', views.TextSearch.as_view()),
    url(r'^license/$', views.Licensing.as_view()),

    # Oauth2 urls
    url(r'^o/', include('api.oauth2_urls', namespace='oauth2_provider')),
]
