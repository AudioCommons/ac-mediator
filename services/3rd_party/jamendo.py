from services.mixins.constants import *
from services.mixins.utils import *
from services.mixins.base import BaseACService
from services.mixins.auth import ACServiceAuthMixin
from services.mixins.search import ACServiceTextSearch, translates_field
from services.mixins.licensing import ACLicensingMixin


class JamendoService(BaseACService, ACServiceAuthMixin, ACServiceTextSearch, ACLicensingMixin):

    # General
    NAME = 'Jamendo'
    URL = 'http://www.jamendo.com'
    API_BASE_URL = 'https://api.jamendo.com/v3.0/'

    # Auth
    SUPPORTED_AUTH_METHODS = [APIKEY_AUTH_METHOD, ENDUSER_AUTH_METHOD]
    BASE_AUTHORIZE_URL = API_BASE_URL + 'oauth/authorize/?client_id={0}'
    ACCESS_TOKEN_URL = API_BASE_URL + 'oauth/grant/'
    REFRESH_TOKEN_URL = API_BASE_URL + 'oauth/grant/'

    def access_token_request_data(self, authorization_code):
        # Jamendo needs to include 'redirect_uri' in the access token request
        data = super(JamendoService, self).access_token_request_data(authorization_code)
        data.update({'redirect_uri': self.get_redirect_uri()})
        return data

    def get_auth_info_for_request(self, auth_method, account=None):
        if auth_method == ENDUSER_AUTH_METHOD:
            return {'params': {'access_token': self.get_enduser_token(account)}}
        else:
            return {'params': {'client_id': self.service_client_id}}

    # Search
    TEXT_SEARCH_ENDPOINT_URL = API_BASE_URL + 'tracks/'

    @property
    def direct_fields_mapping(self):
        return {
            FIELD_ID: 'id',
            FIELD_URL: 'shareurl',
            FIELD_NAME: 'name',
            FIELD_AUTHOR_NAME: 'artist_name',
            FIELD_STATIC_RETRIEVE: 'audiodownload',
        }

    @translates_field(FIELD_TAGS)
    def translate_field_tags(self, result):
        try:
            tags = result['musicinfo']['tags']['genres'] + result['musicinfo']['tags']['instruments'] + result['musicinfo']['tags']['vartags']
        except KeyError:
            tags = []
        return tags

    @translates_field(FIELD_LICENSE)
    def translate_field_license(self, result):
        return translate_cc_license_url(result['license_ccurl'])

    def format_search_response(self, response):
        results = list()
        for result in response['results']:
            results.append(self.translate_single_result(result))
        return {
            NUM_RESULTS_PROP: None,  # TODO: work out this param
            NEXT_PAGE_PROP: None,  # TODO: work out this param
            PREV_PAGE_PROP: None,  # TODO: work out this param
            RESULTS_LIST: results,
        }

    def text_search(self, query):
        # TODO: add minimum response fields?
        response = self.send_request(
            self.TEXT_SEARCH_ENDPOINT_URL,
            params={'search': query, 'include': 'musicinfo+licenses'},
            supported_auth_methods=[APIKEY_AUTH_METHOD]
        )
        return self.format_search_response(response)

    # Licensing
    def get_licensing_url(self, resource_id=None, resource_dict=None):
        if resource_id is None and resource_dict is None:
            raise Exception('Either \'resource_id\' or \'resoruce_dict\' should be provided to \'get_licensing_url\'')
        if resource_dict:
            if resource_dict['licenses']['prolicensing']:
                return resource_dict['prourl']
        # TODO: if resource_dict is not provided then we only get an id, we have to request information
        # TODO: about the id and return url
        return None  # No licensing url available
