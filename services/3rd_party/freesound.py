from ac_mediator.exceptions import ACException
from services.mixins.constants import *
from services.mixins.base import BaseACService
from services.mixins.auth import ACServiceAuthMixin
from services.mixins.search import ACServiceTextSearch


class FreesoundService(BaseACService, ACServiceAuthMixin, ACServiceTextSearch):

    # General settings
    NAME = 'Freesound'
    URL = 'http://www.freesound.org'
    API_BASE_URL = "https://www.freesound.org/apiv2/"

    @staticmethod
    def validate_response_status_code(response):
        if response.status_code != 200:
            raise ACException('{0} error: {1}'.format(response.status_code, response.json()['detail']))
        return response.json()

    # Auth
    SUPPORTED_AUTH_METHODS = [APIKEY_AUTH_METHOD, ENDUSER_AUTH_METHOD]
    BASE_AUTHORIZE_URL = API_BASE_URL + 'oauth2/authorize/?client_id={0}&response_type=code'
    ACCESS_TOKEN_URL = API_BASE_URL + 'oauth2/access_token/'
    REFRESH_TOKEN_URL = API_BASE_URL + 'oauth2/refresh_token/'

    def get_auth_info_for_request(self, auth_method, account=None):
        header_content = 'Token {0}'.format(self.get_apikey())
        if auth_method == ENDUSER_AUTH_METHOD:
            header_content = 'Bearer {0}'.format(self.get_enduser_token(account))
        return {'headers': {'Authorization': header_content}}

    # Search
    TEXT_SEARCH_ENDPOINT_URL = API_BASE_URL + 'search/text/'

    @property
    def direct_fields_mapping(self):
        return {
            'id': FIELD_ID,
            'url': FIELD_URL,
            'name': FIELD_NAME,
            'username': FIELD_AUTHOR_NAME,
            'tags': FIELD_TAGS
        }

    @staticmethod
    def translate_field_license(value):
        return FIELD_LICENSE, {
            'http://creativecommons.org/publicdomain/zero/1.0/': LICENSE_CC0,
            'http://creativecommons.org/licenses/by/3.0/': LICENSE_CC_BY,
            'http://creativecommons.org/licenses/by-nc/3.0/': LICENSE_CC_BY_NC,
            'http://creativecommons.org/licenses/sampling+/1.0/': LICENSE_CC_SAMPLING_PLUS,
        }[value]

    @staticmethod
    def translate_field_previews(value):
        return FIELD_STATIC_RETRIEVE, value['preview-hq-ogg']

    def format_search_response(self, response):
        results = list()
        for result in response['results']:
            results.append(self.translate_single_result(result))
        return {
            NUM_RESULTS_PROP: response['count'],
            NEXT_PAGE_PROP: response['next'],
            PREV_PAGE_PROP: response['previous'],
            RESULTS_LIST: results,
        }

    def text_search(self, query):
        # TODO: add minimum response fields?
        response = self.send_request(
            self.TEXT_SEARCH_ENDPOINT_URL,
            params={'query': query},
            supported_auth_methods=[APIKEY_AUTH_METHOD, ENDUSER_AUTH_METHOD]
        )
        return self.format_search_response(response)
