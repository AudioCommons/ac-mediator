from oauth2_provider.oauth2_validators import OAuth2Validator
from oauth2_provider.models import AbstractApplication


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
        super().validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs)
