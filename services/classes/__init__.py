from accounts.models import ServiceCredentials
from ac_mediator.exceptions import ImproperlyConfiguredACService, ACException
from django.core.urlresolvers import reverse
from django.conf import settings
import requests

# Define some constants (this should come from an ontology definition?)
APIKEY_AUTH_METHOD = 'apikey_auth'
ENDUSER_AUTH_METHOD = 'enduser_auth'


class BaseACService(object):
    """
    Base class for Audio Commons Service.
    An Audio Commons service should be a composition of BaseACService and
    a number of mixins from the classes below (those supported by the service
    api).
    """

    NAME = 'Service name'
    URL = 'http://example.com'
    API_BASE_URL = 'http://example.com/api/'
    service_id = None

    def configure(self, config):
        # Do main configuration
        if 'service_id' not in config:
            raise ImproperlyConfiguredACService('Missing item \'service_id\'')
        self.set_service_id(config['service_id'])

        # Call all object methods that start with 'conf_' to perform mixin's configuration
        for item in dir(self):
            if item.startswith('conf_') and callable(getattr(self, item)):
                getattr(self, item)(config)

    def set_service_id(self, service_id):
        """
        This should be a unique id for the service.
        The id is provided by the Audio Commons consortium.
        :param service_id: 8 character alphanumeric string (e.g. ef21b9ad)
        :return:
        """
        self.service_id = service_id

    @property
    def id(self):
        return self.service_id

    @property
    def name(self):
        return self.NAME

    @property
    def url(self):
        return self.URL


class ACServiceAuthMixin(object):
    """
    Mixin that sotres service credentials and implements service linking steps.
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
        print(settings.BASE_URL + reverse('link_service_callback', args=[self.id]))
        return settings.BASE_URL + reverse('link_service_callback', args=[self.id])

    def access_token_request_data(self, authorization_code):
        return {
            'client_id': self.service_client_id,
            'client_secret': self.service_client_secret,
            'grant_type': 'authorization_code',
            'code': authorization_code
        }

    def request_access_token(self, authorization_code):
        return requests.post(
            self.ACCESS_TOKEN_URL,
            data=self.access_token_request_data(authorization_code)
        )

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
            credentials = ServiceCredentials.objects.get(account=account, service_id=self.id).credentials
            return credentials['access_token']
        except ServiceCredentials.DoesNotExist:
            return None
