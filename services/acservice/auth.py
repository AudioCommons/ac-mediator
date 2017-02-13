from accounts.models import ServiceCredentials
from ac_mediator.exceptions import *
from django.core.urlresolvers import reverse
from django.conf import settings
import requests
from services.acservice.constants import *


class ACServiceAuthMixin(object):
    """
    Mixin that stores service credentials and implements service linking steps.
    This mixin implements standard linking strategy for services that
    support Oauth2 authentication. Services with specific requirements should override
    the methods from this mixin.
    """

    SUPPORTED_AUTH_METHODS = [APIKEY_AUTH_METHOD, ENDUSER_AUTH_METHOD]
    BASE_AUTHORIZE_URL = "http://example.com/api/authorize/?client_id={0}"
    ACCESS_TOKEN_URL = "http://example.com/api/oauth2/access_token/"
    REFRESH_TOKEN_URL = "http://example.com/api/oauth2/refresh_token/"

    service_client_id = None
    service_client_secret = None

    def conf_auth(self, config):
        if 'client_id' not in config:
            raise ImproperlyConfiguredACService('Missing item \'client_id\'')
        if 'client_secret' not in config:
            raise ImproperlyConfiguredACService('Missing item \'client_secret\'')
        self.set_credentials(config['client_id'], config['client_secret'])

    def set_credentials(self, client_id, client_secret):
        self.service_client_id = client_id
        self.service_client_secret = client_secret

    def get_authorize_url(self):
        return self.BASE_AUTHORIZE_URL.format(self.service_client_id)

    def get_redirect_uri(self):
        return settings.BASE_URL + reverse('link_service_callback', args=[self.id])

    def access_token_request_data(self, authorization_code=None, refresh_token=None):
        data = {'client_id': self.service_client_id, 'client_secret': self.service_client_secret}
        if refresh_token is not None:
            # If refresh token is passed, renew using refresh token
            data.update({'grant_type': 'refresh_token', 'refresh_token': refresh_token})
        else:
            # If no refresh token is passed, get access token using authorization code
            if authorization_code is None:
                raise ACException('Authorization code was not provided')
            data.update({'grant_type': 'authorization_code', 'code': authorization_code})
        return data

    def request_access_token(self, authorization_code):
        return requests.post(
            self.ACCESS_TOKEN_URL,
            data=self.access_token_request_data(authorization_code=authorization_code)
        )

    def renew_access_token(self, refresh_token):
        return requests.post(
            self.ACCESS_TOKEN_URL,
            data=self.access_token_request_data(refresh_token=refresh_token)
        )

    def renew_credentials(self, credentials):
        r = self.renew_access_token(self.get_refresh_token_from_credentials(credentials))
        return r.status_code == 200, r.json()

    def request_credentials(self, authorization_code):
        r = self.request_access_token(authorization_code)
        return r.status_code == 200, r.json()

    @staticmethod
    def get_authorize_popup_specs():
        return 'height=400,width=500'

    @staticmethod
    def process_credentials(credentials_data):
        return credentials_data

    def supports_auth(self, auth_type):
        return auth_type in self.SUPPORTED_AUTH_METHODS

    def get_apikey(self):
        """
        API key used for non-end user authenticated requests
        TODO: this should include the way in which the api key is included (via header, request param, etc)
        :return: string containing the api key
        """
        if not self.supports_auth(APIKEY_AUTH_METHOD):
            raise ACException('Auth method \'{0}\' not supported by service {0}'.format(APIKEY_AUTH_METHOD, self.name))
        return self.service_client_secret

    def get_enduser_token(self, account):
        """
        Get token used to make requests to the service on behalf of 'account'
        TODO: this should include the way in which the token is included (via header, request param, etc)
        :param account: user account to act on behalf of
        :return: string containing the token
        """
        if not self.supports_auth(ENDUSER_AUTH_METHOD):
            raise ACException('Auth method \'{0}\' not supported by service {1}'.format(ENDUSER_AUTH_METHOD, self.name))
        try:
            service_credentials = ServiceCredentials.objects.get(account=account, service_id=self.id)
            try:
                self.check_credentials_are_valid(service_credentials)
            except ACAPIInvalidCredentialsForService:
                # Try to renew the credentials
                success, received_credentials = self.renew_credentials(service_credentials)
                if success:
                    # Store credentials (replace existing ones if needed)
                    service_credentials, is_new = ServiceCredentials.objects.get_or_create(
                        account=account, service_id=self.id)
                    service_credentials.credentials = received_credentials
                    service_credentials.save()
                else:
                    raise ACAPIInvalidCredentialsForService(
                        'Could not renew service credentials for {0}'.format(self.name))
            return self.get_access_token_from_credentials(service_credentials)
        except ServiceCredentials.DoesNotExist:
            raise ACAPIInvalidCredentialsForService

    def check_credentials_are_valid(self, credentials):
        """
        Check if the provided credentials are valid for a given service.
        This method should raise ACAPIInvalidCredentialsForServiceException if credentials are not valid.
        This method should be overwritten by each individual service or it will always return true.
        :param credentials: credentials object as stored in ServiceCredentials entry
        """
        return True

    def get_access_token_from_credentials(self, credentials):
        """
        Return the access token from service credentials stored in ServiceCredentials object.
        This method should be overwritten by each individual service that uses access tokens.
        :param credentials: credentials object as stored in ServiceCredentials entry
        :return: access token extracted from the stored credentials
        """
        return None

    def get_refresh_token_from_credentials(self, credentials):
        """
        Return the refresh token from service credentials stored in ServiceCredentials object.
        This method should be overwritten by each individual service that uses access tokens.
        :param credentials: credentials object as stored in ServiceCredentials entry
        :return: refresh token extracted from the stored credentials
        """
        return None

    def get_auth_info_for_request(self, auth_method, account=None):
        """
        Return dictionary with information about how to authenticate a request.
        The dictionary can contain the following fields:
            - header: dictionary with header name and header contents (key, value) to be
              added to a request (including credentials).
            - params: dictionary with request paramer name and contents (key, value) to be
              added to a request (including credentials).
        An example for 'header':
            {'headers': {'Authorization': 'Token API_KEY'}'}
        An example for 'param':
            {'params': {'token': 'API_KEY'}}
        If both fields are included, both will be added when sending the request.
        :param auth_method: auth method for which information is wanted
        :param account: user account (for enduser authentication only)
        :return: dictionary with auth information
        """
        raise NotImplementedError("Service must implement method ACServiceAuthMixin.get_auth_info_for_request")
