from services.classes.constants import *
from services.classes.base import BaseACService
from services.classes.auth import ACServiceAuthMixin
from ac_mediator.exceptions import ImproperlyConfiguredACService


class EuropeanaService(BaseACService, ACServiceAuthMixin):
    NAME = 'Europeana'
    URL = 'http://www.europeana.eu'
    API_BASE_URL = "https://www.europeana.eu/api/"
    SUPPORTED_AUTH_METHODS = [APIKEY_AUTH_METHOD]

    def conf_auth(self, config):
        if 'api_key' not in config:
            raise ImproperlyConfiguredACService('Missing item \'api_key\'')
        self.set_credentials(None, config['api_key'])
