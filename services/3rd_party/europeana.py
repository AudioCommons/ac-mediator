from services.acservice.constants import *
from services.acservice.utils import *
from services.acservice.base import BaseACService
from services.acservice.auth import ACServiceAuthMixin
from services.acservice.search import ACServiceTextSearch, translates_field
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
            FIELD_URL: 'guid',
        }

    @translates_field(FIELD_NAME)
    def translate_field_name(self, result):
        return result['title'][0]

    @translates_field(FIELD_AUTHOR_NAME)
    def translate_field_author_name(self, result):
        try:
            return result['dcCreator'][0]
        except KeyError:
            return None

    @translates_field(FIELD_LICENSE)
    def translate_field_license(self, result):
        return translate_cc_license_url(result['rights'][0])

    @translates_field(FIELD_STATIC_RETRIEVE)
    def translate_field_static_retrieve(self, result):
        # TODO: this field does not always return static file urls...
        return result['edmIsShownBy'][0]

    def format_search_response(self, response, common_search_params):
        results = list()
        warnings = list()
        for result in response['items']:
            translation_warnings, translated_result = \
                self.translate_single_result(result, target_fields=common_search_params.get('fields', None))
            results.append(translated_result)
            if translation_warnings:
                warnings.append(translation_warnings)
        warnings = [item for sublist in warnings for item in sublist]  # Flatten warnings
        warnings = list(set(warnings))  # We don't want duplicated warnings
        return warnings, {
            NUM_RESULTS_PROP: response['totalResults'],
            RESULTS_LIST: results,
        }

    def prepare_search_request(self, q, common_search_params):
        args = [self.TEXT_SEARCH_ENDPOINT_URL]
        kwargs = {'params': {
            'query': q,
            'reusability': 'open',
            'media': 'true',
            'qf': 'TYPE:SOUND',
            'profile': 'rich'
        }}
        return args, kwargs
