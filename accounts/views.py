from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from accounts.forms import RegistrationForm
from services import get_available_services


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
    tvars = {
        'available_services': get_available_services()
    }
    return render(request, 'accounts/link_services.html', tvars)
