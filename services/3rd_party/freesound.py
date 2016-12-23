from ac_mediator.exceptions import ACException
from services.acservice.constants import *
from services.acservice.utils import *
from services.acservice.base import BaseACService
from services.acservice.auth import ACServiceAuthMixin
from services.acservice.search import ACServiceTextSearch, translates_field


class FreesoundService(BaseACService, ACServiceAuthMixin, ACServiceTextSearch):

    # General settings
    NAME = 'Freesound'
    URL = 'http://www.freesound.org'
    API_BASE_URL = "https://www.freesound.org/apiv2/"

    @staticmethod
    def validate_response_status_code(response):
        if response.status_code != 200:
            raise ACException(response.json()['detail'], response.status_code)
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
            FIELD_URL: 'url',
            FIELD_NAME: 'name',
            FIELD_AUTHOR_NAME: 'username',
            FIELD_TAGS: 'tags'
        }

    @translates_field(FIELD_LICENSE)
    def translate_field_license(self, result):
        return translate_cc_license_url(result['license'])

    @translates_field(FIELD_STATIC_RETRIEVE)
    def translate_field_static_retrieve(self, result):
        return result['previews']['preview-hq-ogg']

    def format_search_response(self, response, common_search_params):
        results = list()
        warnings = list()
        for result in response['results']:
            translation_warnings, translated_result = self.translate_single_result(result, target_fields=common_search_params.get('fields', None))
            results.append(translated_result)
            if translation_warnings:
                warnings.append(translation_warnings)
        warnings = [item for sublist in warnings for item in sublist]  # Flatten warnings
        warnings = list(set(warnings))  # We don't want duplicated warnings
        return warnings, {
            NUM_RESULTS_PROP: response['count'],
            RESULTS_LIST: results,
        }

    def prepare_search_request(self, q, common_search_params):
        args = [self.TEXT_SEARCH_ENDPOINT_URL]
        kwargs = {'params': {
            'query': q,
            'fields': 'id,url,name,license,previews,username,tags'
        }}
        # NOTE: we include 'fields' parameter with all Freesound fields that are needed to provide any of the supported
        # Audio Commons fields. This is not optimal in the sense that even if an Audio Commons query only requires field
        # ac:id, the forwarded query to Freesound will request all potential fields. It could be optimized in the future
        # by setting 'fields' depending on what's in common_search_params['fields'].
        return args, kwargs
