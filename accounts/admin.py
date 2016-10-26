from django.contrib import admin
from django.contrib.auth.models import Group
from accounts.models import Account, ServiceCredentials

admin.site.register(Account)
admin.site.register(ServiceCredentials)
admin.site.unregister(Group)  # Remove 'Groups' from admin
