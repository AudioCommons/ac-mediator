from ac_mediator.exceptions import ImproperlyConfiguredACService


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
