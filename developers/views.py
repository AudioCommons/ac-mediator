from oauth2_provider.views.application import ApplicationRegistration as ProviderApplicationRegistration
from oauth2_provider.views.application import ApplicationDetail as ProviderApplicationDetail
from oauth2_provider.views.application import ApplicationList as ProviderApplicationList
from oauth2_provider.views.application import ApplicationDelete as ProviderApplicationDelete
from oauth2_provider.views.application import ApplicationUpdate as ProviderApplicationUpdate
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from api.forms import ApiClientForm
from api.models import ApiClient


class ApplicationRegistration(ProviderApplicationRegistration):
    template_name = "developers/application_registration_form.html"
    success_url = reverse_lazy('developers-app-list')

    def get_form_class(self):
        return ApiClientForm


class ApplicationDetail(ProviderApplicationDetail):
    template_name = "developers/application_detail.html"


class ApplicationList(ProviderApplicationList):
    template_name = "developers/application_list.html"


class ApplicationDelete(ProviderApplicationDelete):
    success_url = reverse_lazy('developers-app-list')
    template_name = "developers/application_confirm_delete.html"


class ApplicationUpdate(ProviderApplicationUpdate):
    template_name = "developers/application_form.html"

    def get_form_class(self):
        return ApiClientForm


@login_required
def application_monitor(request, pk):
    application = get_object_or_404(ApiClient, pk=pk)
    tvars = {'application': application}
    return render(request, 'developers/application_monitor.html', tvars)
