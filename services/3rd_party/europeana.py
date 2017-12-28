from services.acservice.constants import *
from services.acservice.utils import *
from services.acservice.base import BaseACService
from services.acservice.auth import ACServiceAuthMixin
from services.acservice.search import ACServiceTextSearchMixin, translates_field, translates_filter_for_field
from ac_mediator.exceptions import *
import json
import datetime


class EuropeanaService(BaseACService, ACServiceAuthMixin, ACServiceTextSearchMixin):
    NAME = 'Europeana'
    URL = 'http://www.europeana.eu'
    API_BASE_URL = "https://www.europeana.eu/api/v2/"

    # Base
    def validate_response_status_code(self, response):
        if response.status_code != 200:
            try:
                json_contents = response.json()
            except json.decoder.JSONDecodeError:
                json_contents = dict()
            message = json_contents.get('error', 'Unknown error')
            raise ACException(message, response.status_code)
        return response.json()

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

    # Implement fields mapping

    @translates_field(FIELD_URL)
    def translate_field_url(self, result):
        return result['guid'].split('?')[0]

    @translates_field(FIELD_DESCRIPTION)
    def translate_field_description(self, result):
        if 'dcDescription' in result:
            return '\n'.join(result['dcDescription'])
        else:
            return None

    @translates_field(FIELD_COLLECTION_NAME)
    def translate_field_collection_name(self, result):
        if 'europeanaCollectionName' in result:
            return result['europeanaCollectionName'][0]
        else:
            return None

    @translates_field(FIELD_COLLECTION_URL)
    def translate_field_collection_url(self, result):
        collection_name = self.translate_field_collection_name(result)
        if collection_name is not None:
            return \
                'https://www.europeana.eu/portal/en/search?q=europeana_collectionName%3A({0})'.format(collection_name)
        else:
            return None

    @translates_field(FIELD_NAME)
    def translate_field_name(self, result):
        return result['title'][0]

    @translates_field(FIELD_AUTHOR_NAME)
    def translate_field_author_name(self, result):
        try:
            return result['dcCreator'][0]
        except KeyError:
            return None

    @translates_field(FIELD_IMAGE)
    def translate_field_image(self, result):
        try:
            return result['edmPreview'][0]
        except KeyError:
            return None

    @translates_field(FIELD_LICENSE)
    def translate_field_license(self, result):
        return translate_cc_license_url(result['rights'][0])

    @translates_field(FIELD_LICENSE_DEED_URL)
    def translate_field_license_url(self, result):
        return result['rights'][0]

    @translates_field(FIELD_PREVIEW)
    def translate_field_preview(self, result):
        # TODO: this field does not always return static file urls...
        return result['edmIsShownBy'][0]

    @translates_field(FIELD_TIMESTAMP)
    def translate_field_timestamp(self, result):
        return datetime.datetime.strptime(result['timestamp_created'].split('.')[0], '%Y-%m-%dT%H:%M:%S') \
            .strftime(AUDIOCOMMONS_STRING_TIME_FORMAT)

    # Implement filters mapping

    @translates_filter_for_field(FIELD_TIMESTAMP)
    def translate_filter_timestamp(self, value):
        if value == '*':
            return 'timestamp_created', '*'
        return 'timestamp_created', datetime.datetime.strptime(value, AUDIOCOMMONS_STRING_TIME_FORMAT) \
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
        }[operator.upper()]

    # Implement other basic search functions

    def get_results_list_from_response(self, response):
        if not response['items']:
            raise ACAPIPageNotFound
        return response['items']

    def get_num_results_from_response(self, response):
        return response['totalResults']

    def process_q_query_parameter(self, q):
        return {'query': q}

    def process_f_query_parameter(self, f):
        filter_string = self.build_filter_string(f)
        if 'TYPE:SOUND' not in filter_string:
            filter_string += ' TYPE:SOUND'  # Make sure that we always add a filter for the type
        print(filter_string)
        return {'qf': filter_string}

    def process_s_query_parameter(self, s, desc, raise_exception_if_unsupported=False):
        criteria = {
            SORT_OPTION_CREATED: 'timestamp_created'
        }.get(s, None)
        if criteria is None:
            if raise_exception_if_unsupported:
                raise ACException
            criteria = 'timestamp_created'  # Defaults to score
            self.add_response_warning('Sorting criteria \'{0}\' not supported, using default ({1})'.format(s, criteria))
        if desc:
            criteria += '+desc'
        else:
            criteria += '+asc'
        return {'sort': criteria}

    def process_size_query_parameter(self, size, common_search_params):
        size = int(size)
        if size > 100:  # This is Europena's maximum page size
            self.add_response_warning("Maximum '{0}' is 100".format(QUERY_PARAM_SIZE))
            size = 100
        return {'rows': size}

    def process_page_query_parameter(self, page, common_search_params):
        size = common_search_params.get(QUERY_PARAM_SIZE, None)
        rows_dict = self.process_size_query_parameter(size, common_search_params)
        rows = rows_dict['rows']
        if rows is None:
            rows = 12  # Default size for Europeana
        if (page * rows) + rows > 1000:
            page = int(1000/rows) - 1  # Set page to max allowed, Europeana does not allow paginate over 1000 results
            self.add_response_warning('Can\'t paginate beyond first 1000 results, setting page to {0}'.format(page))
        return {'start': ((page - 1) * rows) + 1}

    def add_extra_search_query_params(self):
        return {
            'reusability': 'open',
            'media': 'true',
            'qf': 'TYPE:SOUND',
            'profile': 'rich',
        }
