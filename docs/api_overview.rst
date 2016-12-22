Overview
========

TODO: general introduction to the API

* General Audio Commons Ecosystem structure: all requests to Audio Commons services are done through the mediator
* What types of services there are, i.e., what things the API can do: search, licensing, download, etc.


Requests
--------

.. important::
    All requests should be made over **HTTPS** and pointed to he following
    base URL: ``https://m.audiocommons.org/api/v1``. Trying to access the API over
    HTTP will return an error response.


Audio Commons API Authentication
********************************

To access the Audio Commons API you first need to **request API credentials** (client) in
the Audio Commons mediator `API clients management <http://m.audiocommons.org/developers/clients/>`_ page.

All requests made to the Audio Commons API must be authenticated using **OAuth2** and
the credentials you'll have been given. The Audio Commons API supports different OAuth2
authorization grants (or *flows*) that developers can choose when requesting the API credentials.
Please see the :ref:`api_authentication` documentation for more information.


Authentication in third party services
**************************************

As explained above, practically all interactions between your application and the Audio Commons
Ecosystem will happen through the mediator (will be *mediated* by the mediator).
Hence, the mediator will talk to third party services on behalf of your application and you
won't need to worry about how individual services work.

Nevertheless, there are some situations in which the third party services will require the
**authentication of an end user** in order to respond to the request. For example, if a resource needs
to be uploaded to a third party service, such resource probably needs to be linked to an individual
user account and therefore the upload request to the third party service must be authenticated to
act on behalf of a user account from the service.

Your requests to the Audio Commons API are made using OAuth2, meaning that Audio Commons
registered end users can authenticate themselves in the request. In order to also allow end user
authentication in the third party services, Audio Commons users can **link their Audio Commons user
accounts with third party services accounts**. If accounts are linked the Audio Commons mediator
can forward requests to third party services and authenticate the corresponding end user.
Accounts can be linked in the `Link Services <https://m.audiocommons.org/link_services/>`_
Audio Commons mediator page.

If a request is made to the Audion Commons API that needs to be forwarded to a third party
service with an authenticated end user, and the Audio Commons user account has not been linked
with such third party service user account, an error response will be returned for that
individual service indicating that end user authentication is required.

TODO: illustrate this part with some diagrams might make it clearer



Responses
---------

.. _aggregated-responses:

Aggregated responses
********************

When a request is received, the mediator analyses it and forwards the request to the different third
party services that can provide an answer for it.
Immediately after forwarding the request (and before obtaining any response from the services), the
mediator returns what we call an **aggregated response** dictionary to the application that
made the original request.
This aggregated response includes, among others, the URL that should be followed to retrieve individual
responses returned by the third party services.
The application that sent the original request is therefore responsible for iteratively pulling the
aggregated response contents, which will be updated as soon as new responses are received from
the queried third party services.

An aggregated response will **always** be a dictionary including ``meta``, ``contents``, and ``errors``
keys. This is what should be in each of these keys:


``meta``
++++++++

Will be a dictionary with the following contents:

========================    =====================================================
Key                         Value
========================    =====================================================
``sent_timestamp``          Timestamp corresponding to the moment the request was forwarded by the mediator to the third party services
``n_expected_responses``    Number of expected responses (number of third party services that have been queried)
``n_received_responses``    Number of received responses so far
``status``                  Processing (``PR``) when there are still responses to receive, or Finished (``FI``) when all expected responses have been received
``response_id``             Unique identifier that the Audio Commons mediator gives to the aggregated response
``collect_url``             URL that can be followed to collect updated results
========================    =====================================================

The **most important** property of this dictionary is ``collect_url`` which provides the URL that
must be followed to obtain updated results (if any).
This URL basically redirects to the :ref:`collect-response-endpoint` of the Audio Commons API
with the corresponding ``acid`` query parameter.


``contents``
++++++++++++

This will be a dictionary with the successfully returned responses from individual services.
In this dictionary, keys correspond to service names and corresponding values are the actual
individual responses. The individual contents of each response will depend on the Audio
Commons API endpoint. See the :ref:`endpoints-documentation` for more information.

If all expected individual responses have been received (``status``=``FI``) and no service is able to successfully
deliver a response for the given request, the ``contents`` dictionary will be empty.

.. hint::
    Right after making a request to an Audio Commons API endpoint and receiving the *first* aggregated response,
    the fields ``contents`` and ``error`` will still be empty dictionaries as no individual responses will have
    been received yet.

.. _aggregated-responses-errors:

``errors``
++++++++++

This will be a dictionary with error responses from the individual services.
In this dictionary, keys correspond to service names and corresponding values are the actual
individual error responses. Individual error responses will **always** include the following fields:

======================  =====================================================
Key                     Value
======================  =====================================================
``status_code``         Status code of the error response
``detail``              Message including more details about the error
======================  =====================================================

If no service generates error responses, this dictionary will be empty.


.. warning::
    Note that the status code of the aggregated response will always be 200 OK unless the request was badly formatted
    or an unexpected server error occurred. Errors raised by individual services (such as a resource which is not found)
    are represented for each individual service in the ``errors`` field of the aggregated response. Therefore, error
    checking should be both done at the level of the aggregated response and at the level of the individual services.


Example of a full aggregated response dictionary:

.. code:: json

    {
        "meta": {
            "sent_timestamp": "2016-12-21 16:05:14.696306",
            "n_received_responses": 3,
            "status": "FI",
            "response_id": "9097e3bb-2cc8-4f99-89ec-2dfbe1739e67",
            "collect_url": "https://m.audiocommons.org/api/v1/collect/?rid=9097e3bb-2cc8-4f99-89ec-2dfbe1739e67",
            "n_expected_responses": 3
        },
        "contents": { ... },
        "errors": { ... }
    }

Format
******

All responses are returned in **JSON** format.


Errors
------

If your requests are correctly processed and no errors occur, the Audio Commons API will return a response with a 200 OK status code.
However, if something goes wrong in your requests, the API will return error messages which can include one of the following status codes:

=========================  ====================================================================
HTTP code                  Explanation
=========================  ====================================================================
400 Bad request            The request was unsuccessful because the request is missing parameters or parameters are not properly formatted.
401 Unauthorized           The credentials you provided are invalid.
403 Forbidden              Mainly returned when resources that require HTTPS are accessed with plain HTTP requests.
404 Not found              The information that the request is trying to access does not exist.
405 Method not allowed     The current request method (generally GET or POST) is not supported by the resource.
429 Too many requests      The request was throttled because of exceeding request limit rates (see :ref:`throttling`).
5xx                        An error on our part, hopefully you will see few of these.
=========================  ====================================================================

Similarly to aggregated responses's individual response :ref:`aggregated-responses-errors`, API error responses will consist
of a dictionary with the following contents:

======================  =====================================================
Key                     Value
======================  =====================================================
``status_code``         Status code of the error response (added also here for convenience)
``detail``              Message including more details about the error
======================  =====================================================

.. _throttling:

Throttling
----------

Requests directed to the Audio Commons API are never throttled.
Nevertheless, the requests that the mediator forwards to the individual third party
services **can be throttled** depending on the policies specified by individual service's.

If an individual service throttles one request, this will result in an **429 Too many requests**
error response for the individual service (i.e., in the ``errors`` field of the aggregated response).
The response will include information about the rates that have been violated.


Help
----

TODO: set up public mailing list for API help
