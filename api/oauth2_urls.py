from django.conf.urls import url
from oauth2_provider import views

urlpatterns = (
    url(r'^authorize/$', views.AuthorizationView.as_view(
        template_name='accounts/authorize_client.html',
    ), name="authorize"),
    url(r'^token/$', views.TokenView.as_view(), name="token"),
    url(r'^revoke_token/$', views.RevokeTokenView.as_view(), name="revoke-token"),
)
