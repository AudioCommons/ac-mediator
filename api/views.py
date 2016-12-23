from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound, ParseError
from ac_mediator.exceptions import ACAPIInvalidUrl
from api.request_distributor import get_request_distributor
from api.response_aggregator import get_response_aggregator
from services.management import get_available_services
from services.acservice.constants import SEARCH_TEXT_COMPONENT, LICENSING_COMPONENT, MINIMUM_RESOURCE_DESCRIPTION_FIELDS

request_distributor = get_request_distributor()
response_aggregator = get_response_aggregator()


def parse_request_distributor_query_params(request):
    include = request.GET.get('include', None)
    if include is not None:
        include = include.split(',')

    exclude = request.GET.get('exclude', None)
    if exclude is not None:
        exclude = exclude.split(',')

    wait_until_complete = request.GET.get('wuc', False),  # This option is left intentionally undocumented

    return {key: value for key, value in locals().items() if key in
            ['include', 'exclude', 'wait_until_complete']}


def parse_common_search_query_params(request):
    s = request.GET.get('s', None)
    fields = request.GET.get('fields', None).split(',')
    if fields is None:
        fields = MINIMUM_RESOURCE_DESCRIPTION_FIELDS
    size = request.GET.get('size', 15)
    page = request.GET.get('page', 1)
    offset = request.GET.get('offset', None)

    return {key: value for key, value in locals().items() if key in
            ['s', 'fields', 'size', 'page', 'offset']}


@api_view(['GET'])
def invalid_url(request):
    raise ACAPIInvalidUrl


@api_view(['GET'])
def collect_response(request):
    """
    .. http:get:: /collect/

        Return the contents of the response designated by the query parameter rid.
        See the :ref:`aggregated-responses` section for more information.

        :query rid: response id to collect

        :statuscode 200: no error
        :statuscode 404: response object with the provided id does not exist

        **Response**

        This endpoint returns an aggregated response dictionary as described in the
        :ref:`aggregated-responses` section. As a quick summary, the dictionary include
        the following contents:

        ======================  =====================================================
        Key                     Value
        ======================  =====================================================
        ``meta``                Information about the request such as timestamp and status.
        ``contents``            Dictionary with successfully returned responses from individual services. Keys in the dictionary correspond to service names.
        ``errors``              Dictionary with error responses from the individual services. Keys in the dictionary correspond to service names.
        ======================  =====================================================
    """
    response = response_aggregator.collect_response(request.GET.get('rid'))
    if response is None:
        raise NotFound
    return Response(response)


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

        **Response**

        Response is a dictionary like the example below.
        Note that this endpoint **does not return an aggregated response** but a direct response
        (response does not need to be collected).

        .. code:: json

            {
                "services": {
                    "Freesound": {
                        "id": "aaa099c0",
                        "components": [
                            "text_search"
                        ],
                        "description": {
                            "text_search": {
                                "supported_fields": [
                                    "ac:url",
                                    "ac:author_name",
                                    "ac:id"
                                ]
                            }
                        },
                        "url": "http://www.freesound.org"
                    },
                    "Jamendo": {
                        "id": "tya056c0",
                        "components": [
                            "licensing",
                            "text_search"
                        ],
                        "description": {
                            "text_search": {
                                "supported_fields": [
                                    "ac:url",
                                    "ac:author_name",
                                    "ac:id",
                                    "ac:license"
                                ]
                            }
                        },
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
            'components': service.implemented_components,
            'description': service.get_service_description(),
        } for service in services}
    })


@api_view(['GET'])
def text_search(request):
    """
    .. http:get:: /search/text/

       Documentation for this resource needs to be written.

       .. warning::
            This endpoint returns an aggregated response that needs to be updated by following
            the provided ``collect_url``. See the :ref:`aggregated-responses` section for more information.

       :query q: input query terms
       :query s: sorting criteria
       :query fields: metadata fields to include in each result (names separated by commas)
       :query size: number of results to be included in an individual search response
       :query page: number of results page to retrieve
       :query offset: number of results to skip (this is incompatible with page)
       :query include: services to include in query (names separated by commas)
       :query exclude: services to exclude in query (names separated by commas)

       :statuscode 200: no error (individual responses might have errors, see aggregated response's :ref:`aggregated-responses-errors`)
    """

    distributor_qp = parse_request_distributor_query_params(request)
    search_qp = parse_common_search_query_params(request)
    q = request.GET.get('q', None)  # Textual input query parameter
    if q is None:
        raise ParseError('Missing required query parameter: q')
    response = request_distributor.process_request({
        'component': SEARCH_TEXT_COMPONENT,
        'method': 'text_search',
        'kwargs': dict(q=q, common_search_params=search_qp),
    }, **distributor_qp)
    return Response(response)


@api_view(['GET'])
def licensing(request):
    """
    .. http:get:: /license/

        This endpoint takes as input an Audio Commons Unique Identifier (``acid``) and checks the
        different AC services that implement the licensing components to see whether they can
        provide an URL where the resource can be licensed.

        .. warning::
            This endpoint returns an aggregated response that needs to be updated by following
            the provided ``collect_url``. See the :ref:`aggregated-responses` section for more information.

        :query acid: Audio Commons unique resource identifier
        :query include: services to include in query (names separated by commas)
        :query exclude: services to exclude in query (names separated by commas)

        :statuscode 200: no error (individual responses might have errors, see aggregated response's :ref:`aggregated-responses-errors`)
        :statuscode 400: wrong query parameters provided


        **Response**

        The response of each individual service will simply contain a URL where the given resource can
        be licensed (see example below).
        If no licensing service is able to provide a link for licensing the requested resource, the
        ``contents`` property of the main response will be empty (an empty dictionary).

        .. code:: json

            {
                "meta": {
                    sent_timestamp": "2016-12-22 16:58:55.128886",
                    "current_timestamp": "2016-12-22 16:58:55.158931",
                    "n_received_responses": 1,
                    "status": "FI",
                    "response_id": "9097e3bb-2cc8-4f99-89ec-2dfbe1739e67",
                    "collect_url": "https://m.audiocommons.org/api/v1/collect/?rid=9097e3bb-2cc8-4f99-89ec-2dfbe1739e67",
                    "n_expected_responses": 1
                },
                "contents": {
                    "Jamendo": "https://licensing.jamendo.com/track/1162014"
                },
                "errors": { }
            }
    """

    distributor_qp = parse_request_distributor_query_params(request)
    acid = request.GET.get('acid', None)
    if acid is None:
        raise ParseError('Missing required query parameter: acid')
    response = request_distributor.process_request({
        'component': LICENSING_COMPONENT,
        'method': 'get_licensing_url',
        'kwargs': {'acid': acid}
    }, **distributor_qp)
    return Response(response)
