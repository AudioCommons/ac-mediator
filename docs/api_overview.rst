Overview
========


Requests
--------


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


``errors``
++++++++++

This will be a dictionary with error responses from the individual services.
In this dictionary, keys correspond to service names and corresponding values are the actual
individual error responses. Individual error responses will **always** include the following fields:

======================  =====================================================
Key                     Value
======================  =====================================================
``status``              Status code of the error response
``type``                More specific error type of the response
``message``             Message including more details about the error
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


Throttling
----------


Help
----
