from ac_mediator.exceptions import *
from services.acservice.constants import *
from services.acservice.utils import *
from services.acservice.base import BaseACService
from services.acservice.auth import ACServiceAuthMixin
from services.acservice.search import ACServiceTextSearchMixin, translates_field, translates_filter_for_field
from services.acservice.download import ACDownloadMixin
from accounts.models import Account
import datetime
from django.utils import timezone


class FreesoundService(BaseACService, ACServiceAuthMixin, ACServiceTextSearchMixin, ACDownloadMixin):

    # General settings
    NAME = 'Freesound'
    URL = 'https://freesound.org'
    API_BASE_URL = "https://freesound.org/apiv2/"

    # Base
    def validate_response_status_code(self, response):
        if self.TEXT_SEARCH_ENDPOINT_URL in response.request.url:
            # If request was made to search endpoint, translate 404 to 'page not found exception'
            if response.status_code == 404:
                raise ACAPIPageNotFound
        if 'download/link' in response.request.url:
            # If request was made to download link endpoint, translate 404 to 'resource does not exist'
            if response.status_code == 404:
                raise ACAPIResourceDoesNotExist
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

    def get_refresh_token_from_credentials(self, credentials):
        return credentials.credentials['refresh_token']

    def check_credentials_are_valid(self, credentials):
        date_expired = credentials.modified + datetime.timedelta(seconds=credentials.credentials['expires_in'])
        if timezone.now() > date_expired:
            return False
        return True

    def check_credentials_should_be_renewed_background(self, credentials):
        # Currently, Freesound refresh tokens never expire, therefore credentials never need to be renewed in
        # the background. An expired access token will be automatically renewed at request time.
        return False

    # Search
    TEXT_SEARCH_ENDPOINT_URL = API_BASE_URL + 'search/text/'

    # Implement fields mapping

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
            FIELD_FORMAT: 'type',
            FIELD_COLLECTION_URL: 'pack',
            FIELD_DESCRIPTION: 'description',
            FIELD_LICENSE_DEED_URL: 'license',
        }

    @translates_field(FIELD_LICENSE)
    def translate_field_license(self, result):
        return translate_cc_license_url(result['license'])

    @translates_field(FIELD_PREVIEW)
    def translate_field_preview(self, result):
        return result['previews']['preview-hq-ogg']

    @translates_field(FIELD_IMAGE)
    def translate_field_image(self, result):
        return result['images']['waveform_m']

    @translates_field(FIELD_AUTHOR_URL)
    def translate_field_author_url(self, result):
        return self.API_BASE_URL + 'users/{0}/'.format(result['username'])

    @translates_field(FIELD_TIMESTAMP)
    def translate_field_timestamp(self, result):
        return datetime.datetime.strptime(result['created'].split('.')[0], '%Y-%m-%dT%H:%M:%S')\
            .strftime(AUDIOCOMMONS_STRING_TIME_FORMAT)

    def __translate_ac_field(self, result, field_name, default=None):
        if not result['ac_analysis']:
            return default
        else:
            return result['ac_analysis'].get(field_name, default)

    @translates_field(FIELD_BRIGHTNESS)
    def translate_field_brightness(self, result):
        return self.__translate_ac_field(result, 'ac_brightness')

    @translates_field(FIELD_ROUGHNESS)
    def translate_field_roughness(self, result):
        return self.__translate_ac_field(result, 'ac_roughness')

    @translates_field(FIELD_HARDNESS)
    def translate_field_hardness(self, result):
        return self.__translate_ac_field(result, 'ac_hardness')

    @translates_field(FIELD_SHARPNESS)
    def translate_field_sharpness(self, result):
        return self.__translate_ac_field(result, 'ac_sharpness')

    @translates_field(FIELD_WARMTH)
    def translate_field_warmth(self, result):
        return self.__translate_ac_field(result, 'ac_warmth')

    @translates_field(FIELD_BOOMING)
    def translate_field_booming(self, result):
        return self.__translate_ac_field(result, 'ac_booming')

    @translates_field(FIELD_TEMPO)
    def translate_field_tempo(self, result):
        tempo = self.__translate_ac_field(result, 'ac_tempo')
        if not tempo:
            return None
        return tempo

    @translates_field(FIELD_TEMPO_CONFIDENCE)
    def translate_field_tempo_confidence(self, result):
        return self.__translate_ac_field(result, 'ac_tempo_confidence', default=0.0)

    @translates_field(FIELD_NOTE)
    def translate_field_note(self, result):
        return self.__translate_ac_field(result, 'ac_note')

    @translates_field(FIELD_NOTE_CONFIDENCE)
    def translate_field_note_confidence(self, result):
        return self.__translate_ac_field(result, 'ac_note_confidence', default=0.0)

    @translates_field(FIELD_TONALITY)
    def translate_field_tonality(self, result):
        return self.__translate_ac_field(result, 'ac_tonality')

    @translates_field(FIELD_TONALITY_CONFIDENCE)
    def translate_field_tonality_confidence(self, result):
        return self.__translate_ac_field(result, 'ac_tonality_confidence', default=0.0)

    @translates_field(FIELD_LOUDNESS)
    def translate_field_loudness(self, result):
        return self.__translate_ac_field(result, 'ac_loudness')

    @translates_field(FIELD_SINGLE_EVENT)
    def translate_field_single_event(self, result):
        return self.__translate_ac_field(result, 'ac_single_event')

    @translates_field(FIELD_LOOP)
    def translate_field_loop(self, result):
        return self.__translate_ac_field(result, 'ac_loop')

    # Implement filters mapping

    @property
    def direct_filters_mapping(self):
        return {
            FIELD_CHANNELS: 'channels',
            FIELD_AUTHOR_NAME: 'username',
            FIELD_DURATION: 'duration',
            FIELD_FILESIZE: 'filesize',
            FIELD_BITRATE: 'bitrate',
            FIELD_BITDEPTH: 'bitdepth',
            FIELD_SAMPLERATE: 'samplerate',
            FIELD_TAG: 'tag',
        }

    @translates_filter_for_field(FIELD_ID)
    def translate_filter_id(self, value):
        """
        Implementation for the translation of ID filter. It uses the provided SERVICE_ID_FIELDNAME as key
        for the filter, and removes self.id_prefix from the start of the filter value. This should operate in reverse
        to what `translate_field_id`. In `translate_field_id` we append a prefix to the third party service provided
        id (e.g. 1234 -> prefix:1234). Here we remove that prefix to convert the value to the original (e.g. prefix:1234
        -> 1234).
        """
        return self.SERVICE_ID_FIELDNAME, value[len(self.id_prefix):]

    @translates_filter_for_field(FIELD_FORMAT)
    def translate_filter_format(self, value):
        if value not in ['wav', 'mp3', 'ogg', 'flac', 'aiff']:
            raise ACFilterParsingException(
                'The provided value for filter \'{0}\' is not supported'.format(FIELD_FORMAT))
        return 'type', value

    @translates_filter_for_field(FIELD_LICENSE)
    def translate_filter_license(self, value):
        try:
            license_deed_url = {
                LICENSE_CC_BY: 'Attribution',
                LICENSE_CC_BY_NC: 'Attribution Noncommercial',
                LICENSE_CC0: 'Creative Commons 0',
                LICENSE_CC_SAMPLING_PLUS: 'Sampling+',
            }[value]
        except KeyError:
            raise ACFilterParsingException(
                'The provided value for filter \'{0}\' is not supported'.format(FIELD_LICENSE))
        return 'license', license_deed_url

    @translates_filter_for_field(FIELD_TIMESTAMP)
    def translate_filter_timestamp(self, value):
        if value == '*':
            return 'created', '*'
        return 'created', datetime.datetime.strptime(value, AUDIOCOMMONS_STRING_TIME_FORMAT)\
            .strftime('%Y-%m-%dT%H:%M:%SZ')  # From AC time string format to FS time string format

    def render_filter_term(self, key, value_text=None, value_number=None, value_range=None):
        rendered_value = ''
        if value_text:
            rendered_value = str(value_text)
            if ' ' in rendered_value or '-' in rendered_value:
                rendered_value = '"' + value_text + '"'  # Add quotes if white space present
        elif value_number:
            rendered_value = str(value_number)  # Render string version of value
        elif value_range:
            rendered_value = '[%s TO %s]' % (value_range[0], value_range[1])  # Return range syntax
        return '%s:%s' % (key, rendered_value)

    def render_operator_term(self, operator):
        return {
            'NOT': ' -',
            'OR': ' OR ',
            'AND': ' AND ',
        }[operator]

    # Implement other basic search functions

    def get_results_list_from_response(self, response):
        return response['results']

    def get_num_results_from_response(self, response):
        return response['count']

    def process_q_query_parameter(self, q):
        return {'query': q}

    def process_f_query_parameter(self, f):
        # Call `build_filter_string` from base class, which parses the query filter and builds a new string using
        # the `translates_filter_for_field` and `render_*_term` methods overwritten for Freesound service
        return {'filter': self.build_filter_string(f)}

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
                          'samplerate,type,description,created,pack,images,ac_analysis'}

    # Download component
    DOWNLOAD_ACID_DOMAINS = [NAME]

    def get_download_url(self, context, acid, *args, **kwargs):

        # Translate ac resource id to Freesound resource id
        if not acid.startswith(self.id_prefix):
            raise ACAPIInvalidACID
        resource_id = acid[len(self.id_prefix):]
        try:
            int(resource_id)
        except ValueError:
            raise ACAPIInvalidACID

        response = self.send_request(
            self.API_BASE_URL + 'sounds/{0}/download/link/'.format(resource_id),
            use_authentication_method=ENDUSER_AUTH_METHOD,
            account=Account.objects.get(id=context['user_account_id']),
        )
        return response['download_link']
