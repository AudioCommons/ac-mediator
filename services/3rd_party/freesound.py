from ac_mediator.exceptions import ACException
from services.acservice.constants import *
from services.acservice.utils import *
from services.acservice.base import BaseACService
from services.acservice.auth import ACServiceAuthMixin
from services.acservice.search import ACServiceTextSearch, translates_field
from api.constants import *


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

    def get_results_list_from_response(self, response):
        return response['results']

    def get_num_results_from_response(self, response):
        return response['count']

    def process_q_query_parameter(self, q):
        return list(), {'query': q}

    def process_size_query_parameter(self, size):
        warnings = list()
        size = int(size)
        if size > 150:  # This is Freesound's maximum page size
            warnings.append("Maximum '{0}' for Freesound is 150 items".format(QUERY_PARAM_SIZE))
            size = 150
        return warnings, {'page_size': size}

    def process_page_query_parameter(self, page):
        return list(), {'page': page}

    def add_extra_search_query_params(self):
        # NOTE: we include 'fields' parameter with all Freesound fields that are needed to provide any of the supported
        # Audio Commons fields. This is not optimal in the sense that even if an Audio Commons query only requires field
        # ac:id, the forwarded query to Freesound will request all potential fields. It could be optimized in the future
        # by setting 'fields' depending on what's in common_search_params['fields'].
        return {'fields': 'id,url,name,license,previews,username,tags'}

