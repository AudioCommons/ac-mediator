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

    @property
    def name(self):
        return self.NAME

    @property
    def url(self):
        return self.URL


class ACServiceAuthMixin(object):
    """
    Mixin that defines and implements service linking steps.
    Specific services should override methods from this mixin.
    """

    BASE_AUTHORIZE_URL = "http://example.com/api/authorize/?client_id={client_id}"

    service_client_id = None
    service_client_secret = None

    def set_credentials(self, client_id, client_secret):
        self.service_client_id = client_id
        self.service_client_secret = client_secret

    def get_authorize_url(self):
        return self.BASE_AUTHORIZE_URL.format(self.service_client_id)
