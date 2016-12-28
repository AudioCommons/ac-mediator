from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound, ParseError
from ac_mediator.exceptions import ACAPIInvalidUrl
from api.request_distributor import get_request_distributor
from api.response_aggregator import get_response_aggregator
from services.management import get_available_services
from services.acservice.constants import *


request_distributor = get_request_distributor()
response_aggregator = get_response_aggregator()


def parse_request_distributor_query_params(request):
    include = request.GET.get(QUERY_PARAM_INCLUDE, None)
    if include is not None:
        include = include.split(',')
    exclude = request.GET.get(QUERY_PARAM_EXCLUDE, None)
    if exclude is not None:
        exclude = exclude.split(',')
    wait_until_complete = \
        request.GET.get(QUERY_PARAM_WAIT_UNTIL_COMPLETE, False),  # This option is left intentionally undocumented

    return {
        QUERY_PARAM_INCLUDE: include,
        QUERY_PARAM_EXCLUDE: exclude,
        'wait_until_complete': wait_until_complete,
    }


def parse_common_search_query_params(request):
    fields = request.GET.get(QUERY_PARAM_FIELDS, None).split(',')
    if fields is None:
        fields = MINIMUM_RESOURCE_DESCRIPTION_FIELDS
    size = request.GET.get(QUERY_PARAM_SIZE, 15)
    try:
        size = int(size)
    except ValueError:
        raise ParseError("Invalid '{0}' value".format(QUERY_PARAM_SIZE))
    page = request.GET.get(QUERY_PARAM_PAGE, None)
    if page is not None:
        try:
            page = int(page)
        except ValueError:
            raise ParseError("Invalid '{0}' value".format(QUERY_PARAM_PAGE))
        if page < 1:
            raise ParseError("Invalid '{0}' value (must be greater than 0)".format(QUERY_PARAM_PAGE))
    return {
        QUERY_PARAM_SIZE: size,
        QUERY_PARAM_PAGE: page,
        QUERY_PARAM_FIELDS: fields,
    }


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
        ``warnings``            Dictionary with a list of warnings from each individual services. Keys in the dictionary correspond to service names.
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

        This endpoint allows to perform textual queries in third party content providers.
        It takes an input parameter ``q`` where the textual query is specified plus a number of other
        optional query parameters to define other query aspects (see below).

        .. warning::
            This endpoint returns an aggregated response that needs to be updated by following
            the provided ``collect_url``. See the :ref:`aggregated-responses` section for more information.

        :query q: input query terms
        :query f: filtering criteria (NOT IMPLEMENTED)
        :query s: sorting criteria (NOT IMPLEMENTED)
        :query fields: metadata fields to include in each result (names separated by commas)
        :query size: number of results to be included in an individual search response
        :query page: number of results page to retrieve
        :query include: services to include in query (names separated by commas)
        :query exclude: services to exclude in query (names separated by commas)

        :statuscode 200: no error (individual responses might have errors, see aggregated response's :ref:`aggregated-responses-errors`)

        ``fields`` **parameter**

        Use this parameter to specify the metadata fields that should be included for each item returned
        in the individual search responses. By default only a number of fields will be included (TODO: indicate which
        ones). List needed filter names separated by commas as in the following example:

        .. code-block:: none

            fields=ac:id,ac:name,ac:static_retrieve

        If some fields are requested which can't be returned by an individual service, this will be reported in the
        ``warnings`` section of the aggregated response.

        ``size`` **and** ``page`` **parameters**

        Results returned from search requests are paginated. This means that only a particular number of results
        are returned in the response of the search request, and further results can be requested on demand.
        To decide how many results should be in every page and which page of results to retrieve, you can use
        ``size`` and ``page`` parameters. Both parameters should be integers. Note that some third party services
        might impose different limitations for the size parameter (i.e. not allowing to retrieve more than X
        results at a time). If these limits are reached, this will be reported in the ``warnings`` section of the
        aggregated response.

        If a page number is requested for which no results exist in a given service, this means that all results for
        that particular service will have been retrieved. If that happens, "404 Page Not Found" errors are raised for
        the affected individual services. As expected, these errors are listed in the ``errors`` section of the
        aggregated response.

        **Response**

        The response of each individual service will contain a list of search results including the metadata fields
        indicated using the ``fields`` query parameter (or a default set). Each service will include a ``results``
        list and a ``num_results`` field (which might be null for individual services that don't return a total
        number of results). See the example below with query parameters ``page=1``, ``size=2``,
        ``fields=ac:url,ac:name`` and ``q=music``:

        .. code:: json

            {
               "meta":{
                  "sent_timestamp":"2016-12-28 13:35:08.143439",
                  "status":"FI",
                  "n_expected_responses":2,
                  "collect_url":"https://m.audiocommons.org/api/v1/collect/?rid=4c4b16a5-2def-40c3-98b8-0ce93e492286",
                  "current_timestamp":"2016-12-28 13:35:08.957422",
                  "response_id":"4c4b16a5-2def-40c3-98b8-0ce93e492286",
                  "n_received_responses":2
               },
               "errors":{ },
               "warnings":{ },
               "contents":{
                  "Freesound":{
                     "results":[
                        {
                           "ac:name":"Music Box Melody 1",
                           "ac:url":"https://www.freesound.org/people/undead505/sounds/338986/"
                        },
                        {
                           "ac:name":"Music Box, Happy Birthday.wav",
                           "ac:url":"https://www.freesound.org/people/InspectorJ/sounds/369147/"
                        }
                     ],
                     "num_results":30309
                  },
                  "Europeana":{
                     "results":[
                        {
                           "ac:name":"Santa's Toy factory",
                           "ac:url":"http://www.europeana.eu/portal/record/916107/wws_object_886.html?utm_source=api&utm_medium=api&utm_campaign=qh33gBJ8G"
                        },
                        {
                           "ac:name":"Super 8 Movie Projector - Reverse",
                           "ac:url":"http://www.europeana.eu/portal/record/916107/wws_object_664.html?utm_source=api&utm_medium=api&utm_campaign=qh33gBJ8G"
                        }
                     ],
                     "num_results":12320
                  }
               }
            }
    """

    distributor_qp = parse_request_distributor_query_params(request)
    search_qp = parse_common_search_query_params(request)
    q = request.GET.get(QUERY_PARAM_QUERY, None)  # Textual input query parameter
    if q is None or not q.strip():
        raise ParseError("Missing or invalid query parameter: '{0}'".format(QUERY_PARAM_QUERY))
    f = request.GET.get(QUERY_PARAM_FILTER, None)
    s = request.GET.get(QUERY_PARAM_SORT, None)
    if s is not None and (s not in SORT_OPTIONS and s not in ['-{0}'.format(opt) for opt in SORT_OPTIONS]):
        raise ParseError("Invalid query parameter: '{0}'. Should be one of [{1}]."
                         .format(QUERY_PARAM_SORT, ', '.join(SORT_OPTIONS)))
    response = request_distributor.process_request({
        'component': SEARCH_TEXT_COMPONENT,
        'method': 'text_search',
        'kwargs': dict(q=q, f=f, s=s, common_search_params=search_qp),
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
                    "sent_timestamp": "2016-12-22 16:58:55.128886",
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
                "errors": { },
                "warnings":{ }
            }
    """

    distributor_qp = parse_request_distributor_query_params(request)
    acid = request.GET.get('acid', None)
    if acid is None:
        raise ParseError('Missing required query parameter: acid')
    response = request_distributor.process_request({
        'component': LICENSING_COMPONENT,
        'method': 'license',
        'kwargs': {'acid': acid}
    }, **distributor_qp)
    return Response(response)
