from services.mixins.constants import *
from services.mixins.base import BaseACService
from services.mixins.auth import ACServiceAuthMixin
from services.mixins.search import ACServiceTextSearch


class FreesoundService(BaseACService, ACServiceAuthMixin, ACServiceTextSearch):

    # General settings
    NAME = 'Freesound'
    URL = 'http://www.freesound.org'
    API_BASE_URL = "https://www.freesound.org/apiv2/"

    # Auth
    SUPPORTED_AUTH_METHODS = [APIKEY_AUTH_METHOD, ENDUSER_AUTH_METHOD]
    BASE_AUTHORIZE_URL = API_BASE_URL + 'oauth2/authorize/?client_id={0}&response_type=code'
    ACCESS_TOKEN_URL = API_BASE_URL + 'oauth2/access_token/'
    REFRESH_TOKEN_URL = API_BASE_URL + 'oauth2/refresh_token/'

    def get_auth_info_for_request(self, auth_method, account=None):
        header_content = 'Authorization: Token {0}'.format(self.get_apikey())
        if auth_method == ENDUSER_AUTH_METHOD:
            header_content = 'Authorization: Bearer {0}'.format(self.get_enduser_token(account))
        return {'type': 'header', 'header': header_content}

    # Search
    TEXT_SEARCH_ENDPOINT_URL = API_BASE_URL + 'search/text/'

    @property
    def direct_fields_mapping(self):
        raise dict(
            FIELD_ID='id',
            FIELD_URL='url',
            FIELD_NAME='name',
            FIELD_AUTHOR_NAME='username',
            FIELD_TAGS='tags',
        )

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
        response = self.send_request({
            'method': 'GET',
            'supported_auth_methods': [APIKEY_AUTH_METHOD, ENDUSER_AUTH_METHOD],
            'url': self.TEXT_SEARCH_ENDPOINT_URL,
            'get_params': {'query', query},
            'data': None,
        })
        return self.format_search_response(response)
