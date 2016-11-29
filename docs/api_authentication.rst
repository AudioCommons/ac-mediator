API Authentication
==================

All requests made to the Audio Commons API must be authenticated using OAuth2.
However, the Audio Commons API offers two authorization grants that developers
can choose from at the time of creating an API client:

.. warning:: All requests must be done over **HTTPS**!

User and password grant
-----------------------

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


Three-legged grant
------------------

Step 1
******

Open a browser window pointing to ``https://m.audiocommons.org/api/o/authorize/``
with the following *request parameters*:

======================  =====================================================
Key                     Value
======================  =====================================================
``client_id``           Client id of your API credential
``response_type``       ``code``
======================  =====================================================


Step 2
******

Collect the returned ``code`` and keep it for the next step.


Step 3
******

Make a **POST** request to ``https://m.audiocommons.org/api/o/token/``, and include the following
*body parameters*:

======================  =====================================================
Key                     Value
======================  =====================================================
``client_id``           Client id of your API credentials
``grant_type``          ``password``
``code``                The code obtained in the previous step
``redirect_uri``        One of the valid redirect URIs introduced when creating the credentials
======================  =====================================================

Example response:

.. code-block:: json

    {
      "access_token": "i8fmN4J5El0RL8VdkP9KBE5DewQbA1",
      "expires_in": "86400",
      "token_type": "Bearer",
      "scope": "read write",
      "refresh_token": "sESPwgtP8jGdMg932GdYzUd26dPl73"
    }

Refresh token
*************

Make a **POST** request to ``https://m.audiocommons.org/api/o/token/``, and include the following
*body parameters*:

======================  =====================================================
Name                    Description
======================  =====================================================
``client_id``           Client id of your API credentials
``grant_type``          ``refresh_token``
``refresh_token``       A valid refresh token issued along with a previous access token
======================  =====================================================