from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound, APIException
from rest_framework import status
from api.request_distributor import get_request_distributor
from api.response_aggregator import get_response_aggregator
from services.management import get_available_services
from services.acservice.constants import SEARCH_TEXT_COMPONENT, LICENSING_COMPONENT

request_distributor = get_request_distributor()
response_aggregator = get_response_aggregator()


@api_view(['GET'])
def invalid_url(request):
    raise APIException(detail="Invalid URL", code=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def services(request):
    """
    .. http:get:: /services/

        This endpoint returns information about all third party services available in the Audio
        Commons Ecosystem. For each service, a list of components is provided informing of what
        parts of the Audio Commons API are supported.

        Returned services can be filtered using the ``component`` query parameter.

        :query component: only return services that implement this component

        :statuscode 200: no error

        **Example response**:

        .. code:: json

            {
                "services": {
                    "Freesound": {
                        "id": "aaa099c0",
                        "components": [
                            "text_search"
                        ],
                        "url": "http://www.freesound.org"
                    },
                    "Jamendo": {
                        "id": "tya056c0",
                        "components": [
                            "licensing",
                            "text_search"
                        ],
                        "url": "http://www.jamendo.com"
                    }
                },
                "count": 2
            }
    """
    services = get_available_services(component=request.GET.get('component', None))
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
    .. http:get:: /collect/

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
    .. http:get:: /search/text/

       Documentation for this resource needs to be written.

       :query q: input query terms

       :statuscode 200: no error
    """
    response = request_distributor.process_request({
        'component': SEARCH_TEXT_COMPONENT,
        'method': 'text_search',
        'kwargs': {'query': request.GET.get('q')}
    })
    return Response(response)


@api_view(['GET'])
def licensing(request):
    """
    .. http:get:: /license/

       Documentation for this resource needs to be written.

       :query acid: Audio Commons unique resource identifier

       :statuscode 200: no error
    """
    response = request_distributor.process_request({
        'component': LICENSING_COMPONENT,
        'method': 'get_licensing_url',
        'kwargs': {'acid': request.GET.get('acid')}
    })
    return Response(response)
