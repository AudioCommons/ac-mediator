from django.conf import settings
from django.urls import re_path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from accounts.views import registration, activate_account, resend_activation_emmil
from ac_mediator.views import monitor, crash_me
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


# Auth urls
# https://stackoverflow.com/questions/6930982/how-to-use-a-variable-inside-a-regular-expression
# domainPrefix = "authenticate/"
domainPrefix = ""

urlpatterns = [
    re_path(r'^%scrash/$' % domainPrefix, crash_me, name='crash_me'),
    re_path(r'^%sregister/$' % domainPrefix, registration, name='registration'),
    re_path(r'^%sactivate/(?P<username>[^\/]+)/(?P<uid_hash>[^\/]+)/.*$' % domainPrefix, activate_account, name="accounts-activate"),
    re_path(r'^%sreactivate/$' % domainPrefix, resend_activation_emmil, name="accounts-resend-activation"),
    re_path(r'^%slogin/$' % domainPrefix, auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    re_path(r'^%slogout/$' % domainPrefix, auth_views.LogoutView.as_view(next_page=settings.LOGOUT_URL), name='logout'),
    re_path(r'^%spassword_reset/$' % domainPrefix, auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset_form.html',
            subject_template_name='emails/password_reset_subject.txt',
            email_template_name='emails/password_reset.txt',
        ), name='password_reset'),
    re_path(r'^%spassword_reset/done/$' % domainPrefix, auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ), name='password_reset_done'),
    re_path(r'^%sreset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$' % domainPrefix,
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html'
        ), name='password_reset_confirm'),
    re_path(r'^%sreset/done/$' % domainPrefix, auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ), name='password_reset_complete'),

    # Accounts
    re_path(r'^%s' % domainPrefix, include('accounts.urls')),

    # Developers
    re_path(r'^developers/', include('developers.urls')),

    # Api
    re_path(r'^%sapi/' % domainPrefix, include('api.urls')),

    # Admin
    re_path(r'^admin/monitor/$', monitor, name="admin-monitor"),
    re_path(r'^admin/', admin.site.urls),

    # Documentation
    re_path(r'^docs/', include('docs.urls')),
]

if settings.DEBUG:
    # We need to explicitly add staticfiles urls because we don't use runserver
    # https://docs.djangoproject.com/en/1.10/ref/contrib/staticfiles/#django.contrib.staticfiles.urls.staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
