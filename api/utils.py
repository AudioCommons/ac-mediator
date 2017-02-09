from oauth2_provider.oauth2_validators import OAuth2Validator
from oauth2_provider.models import AbstractApplication
from rest_framework.views import exception_handler
from rest_framework.compat import set_rollback
from rest_framework.response import Response
from rest_framework import status


class ACOAuth2Validator(OAuth2Validator):
    """
    We use a custom OAuth2Validator class so that we can introduce an extra validation check
    for clients trying to authenticate using the password grant. Only clients we trust and to
    whom we've given permission to use password grant can use it.
    """

    def validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs):
        # In case the requested grant_type is 'password', make sure that the API client
        # has password grant enabled (see api.models.ApiClient).
        if grant_type == AbstractApplication.GRANT_PASSWORD and not client.password_grant_is_allowed:
            return False
        # In either case perform validation as implemented in OAuth2Validator
        return super().validate_grant_type(client_id, grant_type, client, request, *args, **kwargs)


def custom_exception_handler(exc, context):
    """
    Custom django rest framework exception handler that includes 'status_code' field in the
    responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Catch unexpected exceptions
    if response is None:
        if isinstance(exc, Exception):
            data = {'detail': 'A server error occurred.'}
            set_rollback()
            response = Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code
    return response
