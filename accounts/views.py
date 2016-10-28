from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from accounts.forms import RegistrationForm
from accounts.models import ServiceCredentials
from services.management import get_available_services, get_service_by_id
from services.mixins.constants import ENDUSER_AUTH_METHOD
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
    linkable_services_info = list()
    non_linkable_services_info = list()
    for service in get_available_services():
        if service.supports_auth(ENDUSER_AUTH_METHOD):
            linkable_services_info.append((
                service,
                service.get_enduser_token(request.user)
            ))
        else:
            non_linkable_services_info.append(service)
    tvars = {'linkable_services_info': linkable_services_info,
             'non_linkable_services_info': non_linkable_services_info}
    return render(request, 'accounts/link_services.html', tvars)


@login_required
def link_service_callback(request, service_id):
    try:
        service = get_service_by_id(service_id)
    except ACServiceDoesNotExist:
        service = None
    code = request.GET.get('code', None)
    if code is None:
        print('There were errors in the redirect from service: {0}'.format(request.GET.get('error', 'unknown')))
    tvars = {
        'errors': service is None or code is None,
        'service_id': service.id if service is not None else None,
        'code': request.GET.get('code'),
        'complete': False,
    }
    return render(request, 'accounts/link_service_callback.html', tvars)


@login_required
def link_service_get_token(request, service_id):
    service = get_service_by_id(service_id)  # No need to check as is called after link_service_callback
    # Request credentials
    success, credentials = service.request_credentials(request.GET.get('code'))
    if success:
        # Store credentials (replace existing ones if needed)
        service_credentials, is_new = ServiceCredentials.objects.get_or_create(
            account=request.user, service_id=service.id)
        service_credentials.credentials = credentials
        service_credentials.save()
    else:
        # Delete credentials (if existing)
        ServiceCredentials.objects.filter(account=request.user, service_id=service_id).delete()
    tvars = {
        'errors': not success,
        'complete': True,
    }
    return render(request, 'accounts/link_service_callback.html', tvars)


@login_required
def unlink_service(request, service_id):
    ServiceCredentials.objects.filter(account=request.user, service_id=service_id).delete()
    return HttpResponseRedirect(reverse('link_services'))
