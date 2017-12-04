from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from accounts.forms import RegistrationForm, ReactivationForm
from accounts.models import ServiceCredentials, Account
from services.management import get_available_services, get_service_by_id
from services.acservice.constants import ENDUSER_AUTH_METHOD
from ac_mediator.exceptions import *
from utils.encryption import create_hash


def registration(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            account = form.save()
            account.is_active = False
            account.save()
            account.send_activation_email()
            return render(request, 'accounts/registration.html', {'form': None})
    else:
        form = RegistrationForm()
    return render(request, 'accounts/registration.html', {'form': form})


def activate_account(request, username, uid_hash):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    try:
        account = Account.objects.get(username__iexact=username)
    except Account.DoesNotExist:
        return render(request, 'accounts/activate.html', {'user_does_not_exist': True})

    new_hash = create_hash(account.id)
    if new_hash != uid_hash:
        return render(request, 'accounts/activate.html', {'decode_error': True})

    account.is_active = True
    account.save()
    return render(request, 'accounts/activate.html', {'all_ok': True})


def resend_activation_emmil(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    if request.method == 'POST':
        form = ReactivationForm(request.POST)
        if form.is_valid():
            account = form.cleaned_data['account']
            account.send_activation_email()
            return render(request, 'accounts/resend_activation.html', {'form': None})
    else:
        form = ReactivationForm()
    return render(request, 'accounts/resend_activation.html', {'form': form})


@login_required
def home(request):
    return render(request, 'accounts/home.html')


@login_required
def link_services(request):
    linkable_services_info = list()
    non_linkable_services_info = list()
    for service in get_available_services():
        if service.supports_auth(ENDUSER_AUTH_METHOD):
            is_linked = False
            try:
                service.get_enduser_token(request.user)
                is_linked = True
            except (ACException, ACAPIException):
                pass
            linkable_services_info.append((
                service,
                is_linked,
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


def store_service_credentials_helper(credentials, account, service_id):
    # Store credentials (replace existing ones if needed)
    service_credentials, is_new = ServiceCredentials.objects.get_or_create(
        account=account, service_id=service_id)
    service_credentials.credentials = credentials
    service_credentials.save()


@login_required
def link_service_get_token(request, service_id):
    service = get_service_by_id(service_id)  # No need to check as is called after link_service_callback
    # Request credentials
    success, credentials = service.request_credentials(request.GET.get('code'))
    if success:
        store_service_credentials_helper(credentials, request.user, service.id)
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
