from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from services.management import get_service_by_id, get_test_service_configuration
from ac_mediator.exceptions import ACServiceDoesNotExist, ACException
from services.acservice.search import ACServiceTextSearchMixin
from services.acservice.licensing import ACLicensingMixin
from services.acservice.download import ACDownloadMixin
from services.acservice.constants import *
from api.views import get_request_context


@login_required
def test_service(request, service_id):
    try:
        service = get_service_by_id(service_id)
    except ACServiceDoesNotExist:
        raise Http404
    tvars = {'service': service, 'components': service.implemented_components}
    return render(request, 'services/test_service.html', tvars)


def _test_search_component(service, test_config, request):
    query = test_config.get('text_search_query', 'dogs')
    service.clear_response_warnings()
    response = service.text_search(
        context=get_request_context(request), q=query, f=None, s=None, common_search_params={
            'fields': MINIMUM_RESOURCE_DESCRIPTION_FIELDS,
            'size': 10,
            'page': 1,
        })
    warnings = service.collect_response_warnings()
    return JsonResponse(
        {'status': 'OK' if len(warnings) == 0 else 'WR',
         'message': 'Success',
         'warnings': warnings,
         'response': response})


def _test_licensing_component(service, test_config, request):
    resource_id = test_config.get('ac_resource_id_for_licensing')
    service.clear_response_warnings()
    response = service.license(context=get_request_context(request), acid=resource_id)
    warnings = service.collect_response_warnings()
    return JsonResponse(
        {'status': 'OK' if len(warnings) == 0 else 'WR',
         'message': 'Success',
         'warnings': warnings,
         'response': response})


def _test_download_component(service, test_config, request):
    resource_id = test_config.get('ac_resource_id_for_download')
    service.clear_response_warnings()
    response = service.download(context=get_request_context(request), acid=resource_id)
    warnings = service.collect_response_warnings()
    return JsonResponse(
        {'status': 'OK' if len(warnings) == 0 else 'WR',
         'message': 'Success',
         'warnings': warnings,
         'response': response})


@login_required
def test_service_component(request, service_id):
    """
    This view should test an individual component of a service (e.g. search) and
    return results in json format. The main test service page will call (via ajax)
    the test components for the different components of the system and display results
    accordingly.
    """

    try:
        service = get_service_by_id(service_id)
    except ACServiceDoesNotExist:
        raise Http404

    test_config = get_test_service_configuration(service)
    component = request.GET.get('component', None)

    try:
        if component == SEARCH_TEXT_COMPONENT and isinstance(service, ACServiceTextSearchMixin):
            return _test_search_component(service, test_config, request)
        if component == LICENSING_COMPONENT and isinstance(service, ACLicensingMixin):
            return _test_licensing_component(service, test_config, request)
        if component == DOWNLOAD_COMPONENT and isinstance(service, ACDownloadMixin):
            return _test_download_component(service, test_config, request)
    except ACException as e:
        return JsonResponse(
            {'component': component,
             'status': 'FA',
             'message': '{0}: {1}'.format(e.__class__.__name__, e.msg)})
    except NotImplementedError as e:
        return JsonResponse(
            {'component': component,
             'status': 'FA',
             'message': '{0}: {1}'.format(e.__class__.__name__, e)})
    except Exception as e:
        return JsonResponse(
            {'component': component,
             'status': 'FA',
             'message': 'Unhandled exception: {0}, {1}'.format(e.__class__.__name__, e)})
    return JsonResponse(
        {'component': component,
         'status': 'IN',
         'message': 'Invalid or not supported component'})
