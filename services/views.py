from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from services.management import get_service_by_id
from ac_mediator.exceptions import ACServiceDoesNotExist, ACException


@login_required
def test_service(request, service_id):
    try:
        service = get_service_by_id(service_id)
    except ACServiceDoesNotExist:
        raise Http404
    tvars = {'service': service}
    return render(request, 'services/test_service.html', tvars)


@login_required
def test_service_component(request, service_id):
    """
    This view should test an individual component of a service (e.g. search) and
    return results in json format. The main test service page will call (via ajax)
    the test components for the different components of the system and display results
    accordingly.
    """
    # TODO: this is currently just a testing implementation, we need to define all the
    # TODO: different components and also which tests to carry out for each component...
    try:
        service = get_service_by_id(service_id)
    except ACServiceDoesNotExist:
        raise Http404
    component = request.GET.get('component', None)
    if component == 'text_search':
        try:
            response = service.text_search(query='dogs')
            return JsonResponse(
                {'component': component,
                 'status': 'OK',
                 'message': 'success',
                 'response': response})
        except ACException as e:
            return JsonResponse(
                {'component': component,
                 'status': 'FA',
                 'message': str(e)}, status=500)
    return JsonResponse(
        {'component': component,
         'status': 'FA',
         'message': 'invalid component'})
