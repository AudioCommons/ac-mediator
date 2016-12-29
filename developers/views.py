from oauth2_provider.views.application import ApplicationRegistration as ProviderApplicationRegistration
from oauth2_provider.views.application import ApplicationDetail as ProviderApplicationDetail
from oauth2_provider.views.application import ApplicationList as ProviderApplicationList
from oauth2_provider.views.application import ApplicationDelete as ProviderApplicationDelete
from oauth2_provider.views.application import ApplicationUpdate as ProviderApplicationUpdate
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from api.forms import ApiClientForm
from api.models import ApiClient
from services.management import get_available_services
import datetime


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


@login_required
def get_application_monitor_data(request, pk):
    """
    Returns API client usage data to be shown in the monitor page.
    This view should return a JSON response with a 'data' field including a list of API usage event.
    Each event should include a 'date' field with the timestamp as returned by Pythons Datetime.timestamp() object
    (https://docs.python.org/3/library/datetime.html#datetime.datetime.timestamp) and with a 'service' property
    with the service name (to which a request was forwarded).
    """
    #application = get_object_or_404(ApiClient, pk=pk)
    fake_data_points = list()
    today = datetime.datetime.today()
    services = get_available_services()
    import random
    N_FAKE_POINTS = 1000
    DAYS_SPAN = 60
    for i in range(0, N_FAKE_POINTS):
        fake_data_points.append({
            'date': (today - datetime.timedelta(minutes=random.randint(0, 60*24*DAYS_SPAN))).timestamp(),
            'service': random.choice(services).name,
        })
    return JsonResponse({'data': fake_data_points})
