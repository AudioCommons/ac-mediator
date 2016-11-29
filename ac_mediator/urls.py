from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from accounts.views import registration
from ac_mediator.views import monitor
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    # Auth urls
    url(r'^register/$', registration, name='registration'),
    url(r'^login/$', auth_views.login, {'template_name': 'accounts/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': settings.LOGOUT_URL}, name='logout'),

    # Accounts
    url(r'^', include('accounts.urls')),

    # Developers
    url(r'^developers/', include('developers.urls')),

    # Services
    url(r'^services/', include('services.urls')),

    # Api
    url(r'^api/', include('api.urls')),

    # Admin
    url(r'^admin/monitor/$', monitor, name="admin-monitor"),
    url(r'^admin/', admin.site.urls),

    # Documentation
    url(r'^docs/', include('docs.urls')),
]

if settings.DEBUG:
    # We need to explicitly add staticfiles urls because we don't use runserver
    # https://docs.djangoproject.com/en/1.10/ref/contrib/staticfiles/#django.contrib.staticfiles.urls.staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
