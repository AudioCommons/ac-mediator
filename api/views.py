from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from ac_mediator.exceptions import *
from api.request_distributor import get_request_distributor
from api.response_aggregator import get_response_aggregator
from services.mgmt import get_available_services
from services.acservice.constants import *
from django.conf import settings
from accounts.models import Account


request_distributor = get_request_distributor()
response_aggregator = get_response_aggregator()


def get_request_context(request):
    user_account_id = None
    dev_account_id = None
    if hasattr(request, 'successful_authenticator') and request.successful_authenticator:
        # In production API calls this should be always the case as otherwise API returns 401 before reaching here
        user_account_id = request.user.id
        dev_account_id = request.auth.application.user.id
    else:
        # In integration tests or local development it can happen that successful_authenticator does not exist
        # In that case we provide 'fake' context so tests can be carried out correctly
        if request.user.is_authenticated():
            user_account_id = request.user.id
            dev_account_id = user_account_id
        else:
            if settings.DEBUG and settings.ALLOW_UNAUTHENTICATED_API_REQUESTS_ON_DEBUG:
                user_account_id = Account.objects.all()[0].id
                dev_account_id = user_account_id
    return {
        'user_account_id': user_account_id,
        'dev_account_id': dev_account_id,
        # NOTE: we use id's instead of the objects so that the dict can be serialized and passed to Celery
    }


def parse_request_distributor_query_params(request):
    include = request.GET.get(QUERY_PARAM_INCLUDE, None)
    if include is not None:
        include = include.split(',')
    exclude = request.GET.get(QUERY_PARAM_EXCLUDE, None)
    if exclude is not None:
        exclude = exclude.split(',')
    wait_until_complete = \
        request.GET.get(QUERY_PARAM_WAIT_UNTIL_COMPLETE, False)  # This option is left intentionally undocumented
    return {
        QUERY_PARAM_INCLUDE: include,
        QUERY_PARAM_EXCLUDE: exclude,
        'wait_until_complete': wait_until_complete,
    }


def parse_common_search_query_params(request):
    fields = request.GET.get(QUERY_PARAM_FIELDS, None)
    if fields is None:
        fields = MINIMUM_RESOURCE_DESCRIPTION_FIELDS
    else:
        if fields == '*':
            fields = ALL_RESOURCE_DESCRIPTION_FIELDS
        else:
            fields = fields.split(',')
    size = request.GET.get(QUERY_PARAM_SIZE, 15)
    try:
        size = int(size)
    except ValueError:
        raise ACAPIBadRequest("Invalid '{0}' value".format(QUERY_PARAM_SIZE))
    page = request.GET.get(QUERY_PARAM_PAGE, None)
    if page is not None:
        try:
            page = int(page)
        except ValueError:
            raise ACAPIBadRequest("Invalid '{0}' value".format(QUERY_PARAM_PAGE))
        if page < 1:
            raise ACAPIBadRequest("Invalid '{0}' value (must be greater than 0)".format(QUERY_PARAM_PAGE))
    return {
        QUERY_PARAM_SIZE: size,
        QUERY_PARAM_PAGE: page,
        QUERY_PARAM_FIELDS: fields,
    }


def get_service_name_from_acid(acid):
    return acid.split(ACID_SEPARATOR_CHAR)[0]  # Derive service name from ACID

def buildResponse(respDict):
    return Response(
        respDict,
        headers = {
            'Link':
                '</static/data/service_context.jsonld>; ' +
                    'rel="http://www.w3.org/ns/json-ld#context"; ' +
                    'type="application/ld+json", ' +
                '</static/data/api_doc.jsonld>; ' +
                    'rel="http://www.w3.org/ns/hydra/core#apiDocumentation"'
        })

@api_view(['GET', 'POST'])
@permission_classes((AllowAny, ))
def invalid_url(request):
    raise ACAPIInvalidUrl


@api_view(['GET'])
def me(request):
    """
    .. http:get:: /me/

        This resource returns information about the Audio Commons user account linked with
        the access token used to authenticate. This information is useful for a third party
        application to uniquely identify an Audio Commons user account and be able to store
        extra information associated to the account or display user information on screen.

        This endpoint takes no query parameters.

        :statuscode 200: no error
        :statuscode 404: no user is authenticated or the linked user account does not exist

        **Response**

        This endpoint returns a dictionary which includes the following contents:

        ======================  =====================================================
        Key                     Value
        ======================  =====================================================
        ``account_id``          Integer representing a unique identifier for the Audio Commons user account.
        ``username``            Username of the corresponding user account (i.e. the logged in user username).
        ======================  =====================================================
    """
    account_id = get_request_context(request)['user_account_id']
    if account_id is None:
        raise ACAPIResourceDoesNotExist
    try:
        account = Account.objects.get(id=account_id)
        return buildResponse({
            'username': account.username,
            'account_id': account.id,
        })
    except Account.DoesNotExist:
        raise ACAPIResourceDoesNotExist


@api_view(['GET'])
def collect_response(request):
    """
    .. http:get:: /collect/

        Return the contents of the response designated by the query parameter rid.
        See the :ref:`aggregated-responses` section for more information.

        :query rid: response id to collect

        :statuscode 200: no error
        :statuscode 401: no authentication details provided
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
        raise ACAPIResponseDoesNotExist
    return buildResponse(response)


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
        :statuscode 401: no authentication details provided

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
    return buildResponse({
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
        :query f: filtering criteria
        :query s: sorting criteria
        :query fields: metadata fields to include in each result (names separated by commas or '*' for all fields)
        :query size: number of results to be included in an individual search response
        :query page: number of results page to retrieve
        :query include: services to include in query (names separated by commas)
        :query exclude: services to exclude in query (names separated by commas)

        :statuscode 200: no error (individual responses might have errors, see aggregated response's :ref:`aggregated-responses-errors`)
        :statuscode 400: wrong query parameters provided
        :statuscode 401: no authentication details provided


        **Filtering with** ``f`` **parameter**

        Use this parameter to further filter search results that match the input query terms. The Audio Commons API
        allows you to define complex and expressive filters combining different metadata fields. Nevertheless, not all
        third party services support such filters. If a service does not support some of the field names, values or
        filter operators specified with the ``f`` parameter, an error will be raised. A list of filters supported by
        each third party service is provided via the `services description endpoint <#get--services->`_.

        Filters are specified with the following syntax:

        .. code-block:: none

            f=field_name:value

        In some cases, filters can also feature ranges, which can be specified as:

        .. code-block:: none

            f=field_name:[value_form,value_to]

        Filter values can be quoted. This is needed when values contain spaces or other special characters like ``:`` or
        ``-``. In that case, a filter would be written as:

        .. code-block:: none

            f=field_name:"value"
            f=field_name:["value_form","value_to"]

        Filters can be combined using ``OR``, ``AND`` or ``NOT`` operators. Precedence can be indicated using
        parentheses ``()``. Operators are required when adding more than one filter:

        .. code-block:: none

            f=field1_name:value AND field2_name:[value_form,value_to]
            f=(field1_name:value AND field2_name:[value_form,value_to]) OR field_name3:value

        The table below lists the field names that can be used in filters and provides hints on how should the values
        look like. Nevertheless, remember that **not all fields are supported for filtering in all services**. You'll
        need to check which ones are available using the `services description endpoint <#get--services->`_.

        ======================  =====================================================
        Field name              Values description
        ======================  =====================================================
        ``ac:id``               Audio Commons Unique Identifier (ACID).
        ``ac:license``          License of the resource, must be one of [``CC0``, ``BY``, ``BY-NC``, ``BY-ND``, ``BY-SA``, ``BY-NC-SA``, ``BY-NC-ND``].
        ``ac:timestamp``        Creation date of the resource. Must be indicated as a **range** with the format ``['2017-09-27 10:01:22','2017-09-27 10:01:22']`` (see examples below).
        ``ac:duration``         Duration of the audio resource in seconds. Must be indicated as range.
        ``ac:tag``              Tag with which the resource has been tagged, indicated a a string (see examples below).
        ``ac:author``           Name of the author of the resource.
        ``ac:format``           Audio format of the resource. Possible values depend on the third party service.
        ``ac:channels``         Number of channels as an integer. Can be specified as a range.
        ``ac:filesize``         Filesize in bytes. Can be specified as a range.
        ``ac:bitrate``          Bitrate in number of bits per second. Can be specified as a range.
        ``ac:bitdepth``         Number of bits per sample. Can be specified as a range.
        ``ac:samplerate``       Sampling rate. Can be specified as a range.
        ======================  =====================================================


        You can **check the following examples** to have a better understanding about how the filters work:

        .. code-block:: none

            # Filter by license
            /api/v1/search/text/?q=metal&include=Jamendo&f=ac:license:BY-NC-ND
            /api/v1/search/text/?q=dogs&include=Freesound&f=ac:license:CC0 OR ac:license:BY

            # Filter by timestamp
            /api/v1/search/text/?q=dogs&include=Freesound&fields=ac:id,ac:timestamp&f=ac:timestamp:['2017-09-27 10:01:22','2017-09-27 10:01:22']

            # Filter by duration
            /api/v1/search/text/?q=metal&include=Jamendo&fields=ac:id,ac:duration&f=ac:duration:[320,350]

            # Filter by duration and license
            /api/v1/search/text/?q=metal&include=Jamendo&fields=ac:id,ac:license,ac:duration&f=ac:license:BY-NC-ND+AND+ac:duration:[320,350]

            # Filter by tags
            /api/v1/search/text/?q=dogs&include=Freesound&fields=ac:id,ac:tags&f=ac:tag:barking+AND+ac:tag:field-recording

            # Filter by author
            /api/v1/search/text/?q=dogs&include=Jamendo&f=ac:author:"Porpoise"


        **Sorting with** ``s`` **parameter**

        Use this parameter to specify a sorting criteria to be used in the results returned by each
        individual service. The Audio Commons API defines the following sorting options:

        ======================  =====================================================
        Option name             Description
        ======================  =====================================================
        ``relevance``           Some relevance score provided by each individual service.
        ``popularity``          Popularity score provided by each individual service (e.g., based on ratings).
        ``duration``            Duration of the audio resource.
        ``created``             Creation date (or upload date) of the resource.
        ``downloads``           Number of downloads of the audio resource.
        ======================  =====================================================

        By default these options are returned in ascending order. Descending order can be requested by
        appending ``-`` to the option name (e.g., ``-duration`` to get longest resources first).

        Not all sorting options are supported by all services. A list of available ``s`` options for each
        individual service is provided via the `services description endpoint <#get--services->`_.


        **Using the** ``fields`` **parameter**

        Use this parameter to specify the metadata fields that should be included for each item returned
        in the individual search responses. By default only a number of fields will be included (TODO: indicate which
        ones). List needed field names separated by commas as in the following example:

        .. code-block:: none

            fields=ac:id,ac:name,ac:static_retrieve

        If some fields are requested which can't be returned by an individual service, this will be reported in the
        ``warnings`` section of the aggregated response. A list of available ``fields`` for each individual service is
        provided via the `services description endpoint <#get--services->`_.


        **Paginating with** ``size`` **and** ``page`` **parameters**

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
    search_qp = parse_common_search_query_params(request)
    q = request.GET.get(QUERY_PARAM_QUERY, None)  # Textual input query parameter
    if q is None or not q.strip():
        raise ACAPIBadRequest("Missing or invalid query parameter: '{0}'".format(QUERY_PARAM_QUERY))
    f = request.GET.get(QUERY_PARAM_FILTER, None)
    s = request.GET.get(QUERY_PARAM_SORT, None)
    if s is not None and (s not in SORT_OPTIONS and s not in ['-{0}'.format(opt) for opt in SORT_OPTIONS]):
        raise ACAPIBadRequest("Invalid query parameter: '{0}'. Should be one of [{1}].".format(
            QUERY_PARAM_SORT, ', '.join(SORT_OPTIONS)))
    response = request_distributor.process_request({
        'context': get_request_context(request),
        'component': SEARCH_TEXT_COMPONENT,
        'method': 'text_search',
        'kwargs': dict(q=q, f=f, s=s, common_search_params=search_qp),
    }, **parse_request_distributor_query_params(request))
    return buildResponse(response)


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
        :statuscode 400: no service is able to answer your request
        :statuscode 401: no authentication details provided


        **Response**

        The response of each individual service will simply contain a dictionary with a single `license_url` field
        containing the URL where the resource can be licensed (see example below).
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
                    "Jamendo": {
                        "license_url": "https://licensing.jamendo.com/track/1162014"
                    }
                },
                "errors": { },
                "warnings":{ }
            }
    """
    acid = request.GET.get('acid', None)
    if acid is None:
        raise ACAPIBadRequest('Missing required query parameter: acid')
    response = request_distributor.process_request({
        'context': get_request_context(request),
        'component': LICENSING_COMPONENT,
        'method': 'license',
        'kwargs': {'acid': acid}
    }, acid_domain=get_service_name_from_acid(acid), **parse_request_distributor_query_params(request))
    return buildResponse(response)


@api_view(['GET'])
def download(request):
    """
    .. http:get:: /download/

        This endpoint takes as input an Audio Commons Unique Identifier (``acid``) and requests a
        download link to the service that hosts the corresponding resource. The corresponding service
        is derived from the unique identifier. The download URL returned by this endpoint is a URL that
        client can use to download the requested resource directly from the content provider without
        any need for further authentication.

        .. warning::
            Event if this endpoint will only forward the request to one third party service (the one
            that hosts the resource), it still returns an aggregated response that needs to be updated
            with the provided ``collect_url``. See the :ref:`aggregated-responses` section for more information.

        :query acid: Audio Commons unique resource identifier

        :statuscode 200: no error (individual responses might have errors, see aggregated response's :ref:`aggregated-responses-errors`)
        :statuscode 400: wrong query parameters provided
        :statuscode 400: no service is able to answer your request
        :statuscode 401: no authentication details provided


        **Response**

        The response is a standard aggregated response with only one service entry. Service entry consists of a
        dictionary with a single `download_url` field containing the URL where the resource can be downloaded.

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
                    "ExampleService": {
                        "download_url": "https://example.service.org/link/to/download/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ/"
                    }
                },
                "errors": { },
                "warnings":{ }
            }
    """
    acid = request.GET.get('acid', None)
    if acid is None:
        raise ACAPIBadRequest('Missing required query parameter: acid')
    response = request_distributor.process_request({
        'context': get_request_context(request),
        'component': DOWNLOAD_COMPONENT,
        'method': 'download',
        'kwargs': {'acid': acid}
    }, acid_domain=get_service_name_from_acid(acid), **parse_request_distributor_query_params(request))
    return buildResponse(response)
