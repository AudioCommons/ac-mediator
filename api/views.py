from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from api.request_distributor import get_request_distributor
from api.response_aggregator import get_response_aggregator
from services.management import get_available_services
from services.acservice.constants import SEARCH_TEXT_COMPONENT, LICENSING_COMPONENT
from django.conf import settings

request_distributor = get_request_distributor()
response_aggregator = get_response_aggregator()


@api_view(['GET'])
def services(request):
    """
    .. http:get:: /api/services/

       Documentation for this resource needs to be written.
    """
    services = get_available_services()
    return Response({
        'count': len(services),
        'services': {service.name: {
            'id': service.id,
            'url': service.url,
            'components': service.implemented_components
        } for service in services}
    })


@api_view(['GET'])
def collect_response(request):
    """
    .. http:get:: /api/collect/

       Return the contents of the response designated by the query parameter rid

       :query rid: response id to collect

       :statuscode 200: no error
    """
    response = response_aggregator.collect_response(request.GET.get('rid'))
    if response is None:
        raise NotFound
    return Response(response)


@api_view(['GET'])
def text_search(request):
    """
    .. http:get:: /api/search/text/

       Documentation for this resource needs to be written.

       :query q: input query terms
       :query async: whether to return a response id or return the actual contents of the reponse

       :statuscode 200: no error
    """
    response = request_distributor.process_request({
        'component': SEARCH_TEXT_COMPONENT,
        'method': 'text_search',
        'kwargs': {'query': request.GET.get('q')}
    }, async=request.GET.get('async', settings.DEFAULT_ASYNC_VALUE) == '1')
    return Response(response)


@api_view(['GET'])
def licensing(request):
    """
    .. http:get:: /api/license/

       Documentation for this resource needs to be written.

       :query acid: Audio Commons unique resource identifier
       :query async: whether to return a response id or return the actual contents of the reponse

       :statuscode 200: no error
    """
    response_id = request_distributor.process_request({
        'component': LICENSING_COMPONENT,
        'method': 'get_licensing_url',
        'kwargs': {'acid': request.GET.get('acid')}
    }, async=request.GET.get('async', settings.DEFAULT_ASYNC_VALUE) == '1')
    return Response(response)
