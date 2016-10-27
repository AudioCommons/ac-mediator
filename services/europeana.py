from services.classes import *
import requests


class EuropeanaService(BaseACService, ACServiceAuthMixin):
    NAME = 'Europeana'
    URL = 'http://www.europeana.eu'
    API_BASE_URL = "https://www.europeana.eu/api/"
    BASE_AUTHORIZE_URL = API_BASE_URL + 'oauth/authorize/?client_id={0}'
    ACCESS_TOKEN_URL = "https://{0}:{1}@www.europeana.eu/api/oauth/token?grant_type=authorization_code&code={2}"
    REFRESH_TOKEN_URL = ACCESS_TOKEN_URL

    def conf_auth(self, config):
        if 'api_key' not in config:
            raise ImproperlyConfiguredACService('Missing item \'api_key\'')
        if 'private_key' not in config:
            raise ImproperlyConfiguredACService('Missing item \'private_key\'')
        self.set_credentials(config['api_key'], config['private_key'])

    def get_authorize_url(self):
        return self.BASE_AUTHORIZE_URL.format(self.service_client_id) \
               + '&redirect_uri=http://localhost:8000/link_service/{0}/'.format(self.id)

    def request_credentials(self, authorization_code):
        r = requests.get(
            self.ACCESS_TOKEN_URL.format(self.service_client_id, self.service_client_secret, authorization_code),
        )
        return r.json()
