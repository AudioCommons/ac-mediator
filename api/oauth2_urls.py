from django.urls import re_path
from oauth2_provider import views

app_name = 'oauth2_provider'
urlpatterns = [
    re_path(r'^authorize/?$', views.AuthorizationView.as_view(
        template_name='accounts/authorize_client.html',
    ), name="authorize"),
    re_path(r'^token/?$', views.TokenView.as_view(), name="token"),
    re_path(r'^revoke_token/?$', views.RevokeTokenView.as_view(), name="revoke-token"),
]
