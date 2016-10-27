from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from accounts.forms import RegistrationForm
from accounts.models import ServiceCredentials
from services import get_available_services, get_service_by_id
from ac_mediator.exceptions import ACServiceDoesNotExist


def registration(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # TODO: send activation email (and set is_active to False)
            return HttpResponseRedirect(reverse('home'))
    else:
        form = RegistrationForm()
    return render(request, 'accounts/registration.html', {'form': form})


@login_required
def home(request):
    return render(request, 'accounts/home.html')


@login_required
def link_services(request):
    services_info = [
        (service, request.user.get_credentials_for_service(service.id)) for service in get_available_services()
    ]
    tvars = {'services_info': services_info}
    return render(request, 'accounts/link_services.html', tvars)


@login_required
def link_service_callback(request, service_id):
    try:
        service = get_service_by_id(service_id)
    except ACServiceDoesNotExist:
        service = None
    tvars = {
        'errors': service is None,
        'service_id': service.id if service is not None else None,
        'code': request.GET.get('code')
    }
    return render(request, 'accounts/link_service_callback.html', tvars)


@login_required
def link_service_get_token(request, service_id):
    service = get_service_by_id(service_id)  # No need to check as is called after link_service_callback

    # Request credentials
    credentials = service.request_credentials(request.GET.get('code'))

    # Store credentials (replace existing ones if needed)
    service_credentials, is_new = ServiceCredentials.objects.get_or_create(
        account=request.user, service_id=service.id)
    service_credentials.credentials = credentials
    service_credentials.save()

    return render(request, 'accounts/link_service_complete.html')


@login_required
def unlink_service(request, service_id):
    ServiceCredentials.objects.filter(account=request.user, service_id=service_id).delete()
    return HttpResponseRedirect(reverse('link_services'))
