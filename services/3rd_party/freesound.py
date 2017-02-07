from ac_mediator.exceptions import *
from services.acservice.constants import *
from services.acservice.utils import *
from services.acservice.base import BaseACService
from services.acservice.auth import ACServiceAuthMixin
from services.acservice.search import ACServiceTextSearchMixin, translates_field
from services.acservice.download import ACDownloadMixin
import datetime
from django.utils import timezone


class FreesoundService(BaseACService, ACServiceAuthMixin, ACServiceTextSearchMixin, ACDownloadMixin):

    # General settings
    NAME = 'Freesound'
    URL = 'http://www.freesound.org'
    API_BASE_URL = "https://www.freesound.org/apiv2/"

    # Base
    def validate_response_status_code(self, response):
        if self.TEXT_SEARCH_ENDPOINT_URL in response.request.url:
            # If request was made to search endpoint, translate 404 to 'page not found exception'
            if response.status_code == 404:
                raise ACPageNotFound
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

    def get_access_token_from_credentials(self, credentials):
        return credentials.credentials['access_token']

    def check_credentials_are_valid(self, credentials):
        date_expired = credentials.created + datetime.timedelta(seconds=credentials.credentials['expires_in'])
        if timezone.now() > date_expired:
            raise ACException(
                'Linked \'{0}\' credentials have expired for account \'{1}\''.format(self.name,
                                                                                     credentials.account.username))

    # Search
    TEXT_SEARCH_ENDPOINT_URL = API_BASE_URL + 'search/text/'

    @property
    def direct_fields_mapping(self):
        return {
            FIELD_URL: 'url',
            FIELD_NAME: 'name',
            FIELD_AUTHOR_NAME: 'username',
            FIELD_TAGS: 'tags',
            FIELD_DURATION: 'duration',
            FIELD_FILESIZE: 'filesize',
            FIELD_CHANNELS: 'channels',
            FIELD_BITRATE: 'bitrate',
            FIELD_BITDEPTH: 'bitdepth',
            FIELD_SAMPLERATE: 'samplerate',
            FIELD_TYPE: 'type',
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
        return {'query': q}

    def process_s_query_parameter(self, s, desc, raise_exception_if_unsupported=False):
        criteria = {
            SORT_OPTION_RELEVANCE: 'score',
            SORT_OPTION_POPULARITY: 'rating',
            SORT_OPTION_DURATION: 'duration',
            SORT_OPTION_DOWNLOADS: 'duration',
            SORT_OPTION_CREATED: 'created'
        }.get(s, None)
        if criteria is None:
            if raise_exception_if_unsupported:
                raise ACException
            criteria = 'score'  # Defaults to score
            self.add_response_warning('Sorting criteria \'{0}\' not supported, using default ({1})'.format(s, criteria))
        if criteria != 'score':
            if desc:
                criteria += '_desc'
            else:
                criteria += '_asc'
        else:
            if not desc:
                self.add_response_warning('Ascending sorting not supported for \'{0}\' criteria'.format(s))
                if raise_exception_if_unsupported:
                    raise ACException
        return {'sort': criteria}

    def process_size_query_parameter(self, size, common_search_params):
        size = int(size)
        if size > 150:  # This is Freesound's maximum page size
            self.add_response_warning("Maximum '{0}' is 150".format(QUERY_PARAM_SIZE))
            size = 150
        return {'page_size': size}

    def process_page_query_parameter(self, page, common_search_params):
        return {'page': page}

    def add_extra_search_query_params(self):
        # NOTE: we include 'fields' parameter with all Freesound fields that are needed to provide any of the supported
        # Audio Commons fields. This is not optimal in the sense that even if an Audio Commons query only requires field
        # ac:id, the forwarded query to Freesound will request all potential fields. It could be optimized in the future
        # by setting 'fields' depending on what's in common_search_params['fields'].
        return {'fields': 'id,url,name,license,previews,username,tags,duration,filesize,channels,bitrate,bitdepth,'
                          'samplerate,type'}

    # Download component
    def get_download_url(self, acid, account):
        if acid is None:
            raise ACDownloadException(
                '\'acid\' should be provided to \'get_download_url\'', 400)

        # Translate ac resource id to Freesound resource id
        if not acid.startswith(self.id_prefix):
            raise ACDownloadException('Invalid resource id \'{0}\''.format(acid), 400)
        resource_id = acid[len(self.id_prefix):]

        response = self.send_request(
            self.API_BASE_URL + 'sounds/{0}/download/link/'.format(resource_id),
            use_authentication_method=ENDUSER_AUTH_METHOD,
            account=account,
        )
        return response['download_link']
