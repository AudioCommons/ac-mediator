from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from services.management import get_service_by_id, get_test_service_configuration
from ac_mediator.exceptions import ACServiceDoesNotExist, ACException
from services.mixins.search import ACServiceTextSearch
from services.mixins.licensing import ACLicensingMixin

@login_required
def test_service(request, service_id):
    try:
        service = get_service_by_id(service_id)
    except ACServiceDoesNotExist:
        raise Http404
    tvars = {'service': service}
    return render(request, 'services/test_service.html', tvars)


def _test_search_component(service, test_config):
    query = test_config.get('text_search_query', 'dogs')
    response = service.text_search(query=query)
    return JsonResponse(
        {'status': 'OK',
         'message': 'Success',
         'response': response})


def _test_licensing_component(service, test_config):
    response = service.get_licensing_url()
    return JsonResponse(
        {'status': 'OK',
         'message': 'Success',
         'response': response})


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

    test_config = get_test_service_configuration(service)
    component = request.GET.get('component', None)
    try:
        if component == 'text_search' and isinstance(service, ACServiceTextSearch):
            return _test_search_component(service, test_config)
        if component == 'licensing' and isinstance(service, ACLicensingMixin):
            return _test_licensing_component(service, test_config)

    except ACException as e:
        return JsonResponse(
            {'component': component,
             'status': 'FA',
             'message': str(e)}, status=500)
    except NotImplementedError as e:
        return JsonResponse(
            {'component': component,
             'status': 'FA',
             'message': '{0}: {1}'.format(e.__class__.__name__, e)}, status=500)
    except Exception as e:
        return JsonResponse(
            {'component': component,
             'status': 'FA',
             'message': 'Unhandled exception: {0}, {1}'.format(e.__class__.__name__, e)}, status=500)
    return JsonResponse(
        {'component': component,
         'status': 'IN',
         'message': 'Invalid or not supported component'})
