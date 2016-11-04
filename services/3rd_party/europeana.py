from services.mixins.constants import *
from services.mixins.utils import *
from services.mixins.base import BaseACService
from services.mixins.auth import ACServiceAuthMixin
from services.mixins.search import ACServiceTextSearch
from ac_mediator.exceptions import ImproperlyConfiguredACService


class EuropeanaService(BaseACService, ACServiceAuthMixin, ACServiceTextSearch):
    NAME = 'Europeana'
    URL = 'http://www.europeana.eu'
    API_BASE_URL = "https://www.europeana.eu/api/v2/"

    # Auth
    SUPPORTED_AUTH_METHODS = [APIKEY_AUTH_METHOD]

    def conf_auth(self, config):
        if 'api_key' not in config:
            raise ImproperlyConfiguredACService('Missing item \'api_key\'')
        self.set_credentials(None, config['api_key'])

    def get_auth_info_for_request(self, auth_method, account=None):
        return {'params': {'wskey': self.get_apikey()}}

    # Search
    TEXT_SEARCH_ENDPOINT_URL = API_BASE_URL + 'search.json'

    @property
    def direct_fields_mapping(self):
        return {
            FIELD_ID: 'id',
            FIELD_URL: 'guid',
        }

    @staticmethod
    def translate_field_name(result):
        return result['title'][0]

    @staticmethod
    def translate_field_author_name(result):
        try:
            return result['dcCreator'][0]
        except KeyError:
            return None

    @staticmethod
    def translate_field_license(result):
        return translate_cc_license_url(result['rights'][0])

    @staticmethod
    def translate_field_tags(result):
        return []  # Explicitly return no tags

    @staticmethod
    def translate_field_static_retrieve(result):
        # TODO: this field does not always return static file urls...
        return result['edmIsShownBy'][0]

    def format_search_response(self, response):
        results = list()
        for result in response['items']:
            results.append(self.translate_single_result(result))
        return {
            NUM_RESULTS_PROP: response['totalResults'],
            NEXT_PAGE_PROP: None,  # TODO: work out this param
            PREV_PAGE_PROP: None,  # TODO: work out this param
            RESULTS_LIST: results,
        }

    def text_search(self, query):
        # TODO: add minimum response fields?
        response = self.send_request(
            self.TEXT_SEARCH_ENDPOINT_URL,
            params={'query': query,
                    'reusability': 'open',
                    'media': 'true',
                    'qf': 'TYPE:SOUND',
                    'profile': 'rich'
                    },
            supported_auth_methods=[APIKEY_AUTH_METHOD]
        )
        return self.format_search_response(response)
