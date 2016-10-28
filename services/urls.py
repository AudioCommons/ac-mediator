from django.conf.urls import url
from services import views

urlpatterns = [
    url(r'^test/(?P<service_id>[^\/]+)/$', views.test_service, name='test_service'),
    url(r'^test/(?P<service_id>[^\/]+)/component/$', views.test_service_component, name='test_service_component'),
]
