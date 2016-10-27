from ac_mediator.exceptions import ImproperlyConfiguredACService
import requests


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
    Mixin that defines and implements service linking steps.
    This mixin implements standard linking strategy for services that
    implement Oauth2. Services with specific requirements should override
    the methods from this mixin.
    """

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

    def request_credentials(self, authorization_code):
        r = requests.post(
            self.ACCESS_TOKEN_URL,
            data={
                'client_id': self.service_client_id,
                'client_secret': self.service_client_secret,
                'grant_type': 'authorization_code',
                'code': authorization_code
            }
        )
        return r.json()

    @staticmethod
    def process_credentials(credentials_data):
        return credentials_data

    @staticmethod
    def get_authorize_popup_specs():
        return 'height=400,width=500'
