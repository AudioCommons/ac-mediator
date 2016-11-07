from ac_mediator.exceptions import ImproperlyConfiguredACService, ACException
from services.mixins.constants import *
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
    implemented_components = None

    def configure(self, config):
        # Do main configuration
        if 'service_id' not in config:
            raise ImproperlyConfiguredACService('Missing item \'service_id\'')
        self.set_service_id(config['service_id'])

        # Call all object methods that start with 'conf_' to perform mixin's configuration
        self.implemented_components = list()  # Init implemented components to empty list
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

    def send_request(self,
                     url,
                     method='get',
                     params=None,
                     data=None,
                     supported_auth_methods=None,
                     account=None,
                     use_authentication_method=None):
        """
        Make a request to the service. If not provided, this method automatically chooses
        a suitable authentication method for making the request.
        :param method: request method (either 'get' or 'post')
        :param url: endpoint api url
        :param params: request parameters in a dictionary
        :param data: dictionary of data to be included as json body
        :param supported_auth_methods: auth methods supported by the api endpoint
        :param account: user account (for enduser authentication only)
        :return: dictionary of json response (can raise exception if status_code!=200)
        """
        if method not in ['get', 'post']:
            raise ACException('Request method {0} not in allowed methods'.format(method))
        if params is None:
            params = {}
        if data is None:
            data = {}
        if supported_auth_methods is None:
            supported_auth_methods = [APIKEY_AUTH_METHOD, ENDUSER_AUTH_METHOD]
        if use_authentication_method is None:
            if ENDUSER_AUTH_METHOD not in supported_auth_methods:
                auth_method = APIKEY_AUTH_METHOD
            else:
                if account is None:
                    auth_method = APIKEY_AUTH_METHOD
                else:
                    auth_method = ENDUSER_AUTH_METHOD
        else:
            if use_authentication_method not in supported_auth_methods:
                raise ACException('Authentication method {0} not supported by endpoint'.format(use_authentication_method))
            auth_method = use_authentication_method

        auth_info = self.get_auth_info_for_request(auth_method, account=account)
        params.update(auth_info.get('params', dict()))  # Update current params with auth params (if any)
        r = getattr(requests, method)(
            url,
            params=params,
            data=data,
            headers=auth_info.get('headers', dict()))
        return self.validate_response_status_code(r)

    @staticmethod
    def validate_response_status_code(response):
        """
        Process service API responses and raise exceptions if errors occur.
        Otherwise return response as dictionary object loaded from json contents.
        This base class contains a basic implementation of this method that raises
        generic exceptions without explanation or details. Services will want to override
        this method to better interpret the way errors are returned.
        :param response: response object (of type requests.models.Response)
        :return: dictioanry including json contents of the response
        """
        if response.status_code != 200:
            raise ACException('Returned wrong status code, {0}'.format(response.status_code))
        return response.json()

    @property
    def id(self):
        return self.service_id

    @property
    def name(self):
        return self.NAME

    @property
    def url(self):
        return self.URL
