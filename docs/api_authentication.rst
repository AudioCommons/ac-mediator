API Authentication
==================

All requests made to the Audio Commons API must be authenticated using OAuth2.
However, the Audio Commons API offers two authorization grants that developers
can choose from at the time of creating an API client:

.. warning:: All requests must be done over **HTTPS**!


Register new API application
----------------------------

New API applications (or clients) must be registered at ``http://m.audiocommons.org/developers/clients/``

Types of applications:

* **Public client with implicit grant**: Lorem ipsum dolor sit amet, consectetur adipiscing
  labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco
  laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in
  voluptate velit esse cillum dolore eu


* **Confidential client with authorization code grant**: Lorem ipsum dolor sit amet, consectetur
  labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco
  laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in
  voluptate velit esse cillum dolore eu


* **Public client with password grant**: Lorem ipsum dolor sit amet, consectetur adipiscing elit,
  labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco
  laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in
  voluptate velit esse cillum dolore eu


OAuth2 flows
------------

Password grant
**************

Make a **POST** request to ``https://m.audiocommons.org/api/o/token/``, and include the following
*body parameters*:

======================  =====================================================
Key                     Value
======================  =====================================================
``client_id``           Client id of your API credentials
``grant_type``          ``password``
``username``            Username of the end user
``password``            Password of the end user
======================  =====================================================


Example response:

.. code-block:: json

    {
      "access_token": "i8fmN4J5El0RL8VdkP9KBE5DewQbA1",
      "expires_in": "86400",
      "token_type": "Bearer",
      "scope": "read",
      "refresh_token": "sESPwgtP8jGdMg932GdYzUd26dPl73"
    }


The response includes the following access token information:

======================  =====================================================
Key                     Value
======================  =====================================================
``access_token``        The access token to use in your future requests
``refresh_token``       Refresh token that can be used to renew your access token (see below)
``token_type``          ``Bearer``
``expires_in``          Lifetime of the token in seconds, typically ``86400``(10 minutes)
``scope``               Scopes to which the token gives access (defaults to ``read``)
======================  =====================================================


.. warning:: Because password grant is used with public client, it **must not** use ``client_secret`


Authorization code grant
************************

**Step 1**

Open a browser window pointing to ``https://m.audiocommons.org/api/o/authorize/``
with the following *request parameters*:

======================  =====================================================
Key                     Value
======================  =====================================================
``client_id``           Client id of your API credential
``response_type``       ``code``
``state``               Optional string that will be returned in the redirect
======================  =====================================================


**Step 2**

Users will be shown a page which asks them if they agree on giving your application permission
to act on their behalf. Furthermore, if users are not logged in, they'll be redirected to the
login page before.

Once users click on **Allow**, the browser page will be redirected **redirect_uri**
which was provided at application registration time. This redirect will include a ``code``
request parameter which must be used for the next step. If there are errors, the redirect
will include a ``error`` parameter instead. If ``state`` was included in step 1,
a ``state`` with the same contents will also be added as a get parameter in the redirect.



**Step 3**

Make a **POST** request to ``https://m.audiocommons.org/api/o/token/``, and include the following
*body parameters*:

======================  =====================================================
Key                     Value
======================  =====================================================
``client_id``           Client id of your API credentials
``client_secret``       Client secret of your API credentials
``grant_type``          ``authorization_code``
``code``                The code obtained in the previous step
``redirect_uri``        One of the valid redirect URIs introduced when creating the credentials
======================  =====================================================


Example response:

.. code-block:: json

    {
      "access_token": "i8fmN4J5El0RL8VdkP9KBE5DewQbA1",
      "expires_in": "86400",
      "token_type": "Bearer",
      "scope": "read",
      "refresh_token": "sESPwgtP8jGdMg932GdYzUd26dPl73"
    }


The response includes the following access token information:

======================  =====================================================
Key                     Value
======================  =====================================================
``access_token``        The access token to use in your future requests
``refresh_token``       Refresh token that can be used to renew your access token (see below)
``token_type``          ``Bearer``
``expires_in``          Lifetime of the token (in seconds)
``scope``               Scopes to which the token gives access (defaults to ``read``)
======================  =====================================================


Implicit grant
**************

The implicit grant is a simplification of the authorization code grant better suited for applications
running in browsers or mobile devices.

**Step 1**

Open a browser window pointing to ``https://m.audiocommons.org/api/o/authorize/``
with the following *request parameters*:

======================  =====================================================
Key                     Value
======================  =====================================================
``client_id``           Client id of your API credential
``response_type``       ``token``
``state``               Optional string that will be returned in the redirect
======================  =====================================================

**Step 2**

Users will be shown a page which asks them if they agree on giving your application permission
to act on their behalf. Furthermore, if users are not logged in, they'll be redirected to the
login page before.

Once users click on **Allow**, the browser page will be redirected **redirect_uri**
which was provided at application registration time. This redirect will include access token information
in the form of a number of parameters in the *fragment* part of the url, i.e. after the *#*. See the following
example redirect url:

.. code-block:: json

    https://example.com#access_token=SOfTfmqMmyiaUEGdLAZqZ3Gn0bEKA2&token_type=Bearer&expires_in=86400&state=an_optional_state&scope=read


Similarly to the other flows, the returned access token information is:

======================  =====================================================
Key                     Value
======================  =====================================================
``access_token``        The access token to use in your future requests
``token_type``          ``Bearer``
``expires_in``          Lifetime of the token in seconds, typically ``86400``(10 minutes)
``scope``               Scopes to which the token gives access (defaults to ``read``)
``state``               The same string used in step 1 (or an empty string if no state was provided)
======================  =====================================================

The implicit grant does not require the third step of the authorization code grant.

.. warning:: Because password grant is used with public client, it **must not** use ``client_secret`

.. warning:: As indicated in RFC 6749, the implicit grant **does not** issue a refresh token!



Refreshing tokens
*****************

Make a **POST** request to ``https://m.audiocommons.org/api/o/token/``, and include the following
*body parameters*:

======================  =====================================================
Name                    Description
======================  =====================================================
``client_id``           Client id of your API credentials
``grant_type``          ``refresh_token``
``refresh_token``       A valid refresh token (issued when first requesting the access token)
======================  =====================================================