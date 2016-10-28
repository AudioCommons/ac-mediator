from django.shortcuts import render
from django.http import Http404
from django.contrib.auth.decorators import login_required
from services.management import get_service_by_id
from ac_mediator.exceptions import ACServiceDoesNotExist


@login_required
def test_service(request, service_id):
    try:
        service = get_service_by_id(service_id)
    except ACServiceDoesNotExist:
        raise Http404
    tvars = {'service': service}
    return render(request, 'services/test_service.html', tvars)
