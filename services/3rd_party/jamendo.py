from ac_mediator.exceptions import *
from services.acservice.constants import *
from services.acservice.utils import *
from services.acservice.base import BaseACService
from services.acservice.auth import ACServiceAuthMixin
from services.acservice.search import ACServiceTextSearchMixin, translates_field, translates_filter_for_field
from services.acservice.licensing import ACLicensingMixin
from services.acservice.download import ACDownloadMixin
import datetime
import urllib


class JamendoService(BaseACService, ACServiceAuthMixin, ACServiceTextSearchMixin, ACLicensingMixin, ACDownloadMixin):

    # General
    NAME = 'Jamendo'
    URL = 'http://www.jamendo.com'
    API_BASE_URL = 'https://api.jamendo.com/v3.0/'

    # Auth
    SUPPORTED_AUTH_METHODS = [APIKEY_AUTH_METHOD, ENDUSER_AUTH_METHOD]
    BASE_AUTHORIZE_URL = API_BASE_URL + 'oauth/authorize/?client_id={0}'
    ACCESS_TOKEN_URL = API_BASE_URL + 'oauth/grant/'
    REFRESH_TOKEN_URL = API_BASE_URL + 'oauth/grant/'

    def access_token_request_data(self, authorization_code=None, refresh_token=None):
        # Jamendo needs to include 'redirect_uri' in the access token request
        data = super(JamendoService, self).access_token_request_data(
            authorization_code=authorization_code, refresh_token=refresh_token)
        data.update({'redirect_uri': self.get_redirect_uri()})
        return data

    def get_auth_info_for_request(self, auth_method, account=None):
        if auth_method == ENDUSER_AUTH_METHOD:
            return {'params': {'access_token': self.get_enduser_token(account)}}
        else:
            return {'params': {'client_id': self.service_client_id}}

    # Search
    TEXT_SEARCH_ENDPOINT_URL = API_BASE_URL + 'tracks/'

    # Implement fields mapping

    @property
    def direct_fields_mapping(self):
        return {
            FIELD_URL: 'shareurl',
            FIELD_NAME: 'name',
            FIELD_AUTHOR_NAME: 'artist_name',
            FIELD_PREVIEW: 'audiodownload',
            FIELD_IMAGE: 'image',
            FIELD_DURATION: 'duration',
            FIELD_LICENSE_DEED_URL: 'license_ccurl',
            FIELD_WAVEFORM_PEAKS: 'waveform' 
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

    @translates_field(FIELD_TIMESTAMP)
    def translate_field_timestamp(self, result):
        return datetime.datetime.strptime(result['releasedate'], '%Y-%m-%d').strftime(AUDIOCOMMONS_STRING_TIME_FORMAT)

    # Implement filters mapping

    @translates_filter_for_field(FIELD_TAG)
    def translate_filter_tag(self, value):
        return 'tag_filter', value

    @translates_filter_for_field(FIELD_FORMAT)
    def translate_filter_format(self, value):
        if value not in ['mp31', 'mp32', 'ogg', 'flac']:
            raise ACFilterParsingException(
                'The provided value for filter \'{0}\' is not supported'.format(FIELD_FORMAT))
        return 'type', value

    @translates_filter_for_field(FIELD_ID)
    def translate_filter_id(self, value):
        return 'filter_id', value[len(self.id_prefix):]

    @translates_filter_for_field(FIELD_LICENSE)
    def translate_filter_license(self, value):
        # We use this function to translate from AC license names to the combinations of parameters that are used in
        # Jamendo to produce the same results (see self.process_f_query_parameter() to better understand this part).
        try:
            license_bool_params = {
                LICENSE_CC_BY: '',
                LICENSE_CC_BY_SA: 'ccsa',
                LICENSE_CC_BY_NC: 'ccnc',
                LICENSE_CC_BY_ND: 'ccnd',
                LICENSE_CC_BY_NC_SA: 'ccsa,ccnc',
                LICENSE_CC_BY_NC_ND: 'ccnc,ccnd',
            }[value]
        except KeyError:
            raise ACFilterParsingException(
                'The provided value for filter \'{0}\' is not supported'.format(FIELD_LICENSE))
        return 'license_filter', license_bool_params

    @translates_filter_for_field(FIELD_DURATION)
    def translate_filter_duration(self, value):
        return 'duration_filter', int(value)  # Round value to int

    @translates_filter_for_field(FIELD_AUTHOR_NAME)
    def translate_filter_author(self, value):
        return 'author_filter', value

    @translates_filter_for_field(FIELD_TIMESTAMP)
    def translate_filter_timestamp(self, value):
        return 'timestamp_filter', datetime.datetime.strptime(value, AUDIOCOMMONS_STRING_TIME_FORMAT)\
            .strftime('%Y-%m-%d')  # From AC time string format to Jamendo time string format

    def render_filter_term(self, key, value_text=None, value_number=None, value_range=None):
        rendered_value = ''
        if value_text:
            rendered_value = urllib.parse.quote(str(value_text), safe='')
        elif value_number:
            rendered_value = str(value_number)  # Render string version of value
        elif value_range:
            rendered_value = '%s_%s' % (value_range[0], value_range[1])  # Return range syntax
        return '%s:%s' % (key, rendered_value)

    def render_operator_term(self, operator):
        if operator != 'AND':
            raise ACFilterParsingException('Filtering only supports "AND" operators')
        else:
            return '&&&'

    # Implement other basic search functions

    def get_results_list_from_response(self, response):
        return response['results']

    def get_num_results_from_response(self, response):
        return response['headers']['results_fullcount']

    def process_q_query_parameter(self, q):
        return {'search': q}

    def process_f_query_parameter(self, f):
        # The way in which filtering works in Jamendo API as compared to Freesound is quite different. Freesound
        # supports filters through a query param to which expressions can be passed. Jamendo supports a number of
        # specific filters which are passed as different query parameters and are always ANDed. We configure the
        # filter parser rendered for the Jamendo service to only allow AND operators and to render the AND operator
        # as '&&&'. In this way we build a filter string which is easy to parse afterwards. We split the filter string
        # by '&&&' and process each supported field accordingly. This works in combination with the functions
        # 'translates_filter_for_field' which transform the AudioCommons field names and values to some information
        # which is passed and interpreted here.
        filter_params = {}
        for item in self.build_filter_string(f).split('&&&'):
            if 'license_filter:' in item:
                filter_params.update({
                    'ccsa': 'false',
                    'ccnc': 'false',
                    'ccnd': 'false',
                })
                # Add necessary query params to create license filter
                if 'ccsa' in item:
                    filter_params['ccsa'] = 'true'
                if 'ccnc' in item:
                    filter_params['ccnc'] = 'true'
                if 'ccnd' in item:
                    filter_params['ccnd'] = 'true'
            if 'duration_filter' in item:
                filter_params.update({
                    'durationbetween': item.split('duration_filter:')[1],
                })
            if 'timestamp_filter' in item:
                filter_params.update({
                    'datebetween': item.split('timestamp_filter:')[1],
                })
            if 'filter_id' in item:
                filter_params.update({
                    'id': item.split('filter_id:')[1],
                })
            if 'author_filter' in item:
                filter_params.update({
                    'artist_name': item.split('author_filter:')[1],
                })
            if 'tag_filter' in item:
                if 'tags' in filter_params:
                    filter_params['tags'] += '+' + item.split('tag_filter:')[1]
                else:
                    filter_params.update({
                        'tags': item.split('tag_filter:')[1],
                    })
        return filter_params

    def process_size_query_parameter(self, size, common_search_params):
        size = int(size)
        if size > 200:  # This is Jamendo's maximum page size
            self.add_response_warning("Maximum '{0}' is 200".format(QUERY_PARAM_SIZE))
            size = 200
        return {'limit': size}

    def process_page_query_parameter(self, page, common_search_params):
        # NOTE: Jamendo uses an offset/limit approach to pagination instead of page_size/page_number, therefore to
        # estimate the page number we need to know the requested size of the page

        size = common_search_params[QUERY_PARAM_SIZE]
        if size is not None:  # size defaults to 15 so it should never be 'None'
            used_size = self.process_size_query_parameter(size, common_search_params)['limit']
        else:
            used_size = 10  # Jamendo's default
        print(used_size, used_size * (page - 1) )
        return {'offset': used_size * (page - 1)}

    def add_extra_search_query_params(self):
        # Use include parameter to retrieve all infomation we need and fullcount to get total number of results
        return {'include': 'musicinfo+licenses', 'fullcount': 'true'}

    # Licensing
    LICENSING_ACID_DOMAINS = [NAME]

    def get_licensing_url(self, context, acid, *args, **kwargs):
        if not acid.startswith(self.id_prefix):
            raise ACAPIInvalidACID
        resource_id = acid[len(self.id_prefix):]
        response = self.send_request(
            self.TEXT_SEARCH_ENDPOINT_URL,
            params={'id': resource_id, 'include': 'licenses'},
        )
        if response['headers']['results_count'] == 0:
            raise ACAPIResourceDoesNotExist
        return response['results'][0].get('prourl', None)

    # Download
    DOWNLOAD_ACID_DOMAINS = [NAME]

    def get_download_url(self, context, acid, *args, **kwargs):

        # Translate ac resource id to Jamendo resource id
        if not acid.startswith(self.id_prefix):
            raise ACAPIInvalidACID
        resource_id = acid[len(self.id_prefix):]
        try:
            int(resource_id)
        except ValueError:
            raise ACAPIInvalidACID

        response = self.send_request(
            self.API_BASE_URL + 'tracks/',
            params={'id': resource_id}
        )
        # This is a simple implementation of the service which simply returns a preview download url
        # Ideally this should return a link to the original quality file which does not include the
        # client id, etc (which can be retrieved without authorisation in the client)
        return response['results'][0]['audiodownload']
