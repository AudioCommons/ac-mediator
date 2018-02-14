from api.constants import *

# String used to be the base of ACIDs
# Param substitution will be used to provide a service-specific prefix to the id
ACID_SEPARATOR_CHAR = ':'

# Some of these concept definitions should be linked with the ontology (or be loaded from it)
AUDIOCOMMONS_ONTOLOGY_PREFIX = 'ac:'

# Component names
SEARCH_TEXT_COMPONENT = 'text_search'
LICENSING_COMPONENT = 'licensing'
DOWNLOAD_COMPONENT = 'download'

# Service description keywords
ACID_DOMAINS_DESCRIPTION_KEYWORD = 'acid_domains'
SUPPORTED_FIELDS_DESCRIPTION_KEYWORD = 'supported_fields'
SUPPORTED_FILTERS_DESCRIPTION_KEYWORD = 'supported_filters'
SUPPORTED_SORT_OPTIONS_DESCRIPTION_KEYWORD = 'supported_sort_options'

# Authentication
APIKEY_AUTH_METHOD = 'apikey_auth'
ENDUSER_AUTH_METHOD = 'enduser_auth'

# Resource fields (just using fake names here)
FIELD_ID = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'id'
FIELD_URL = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'url'
FIELD_NAME = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'name'
FIELD_AUTHOR_NAME = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'author'
FIELD_AUTHOR_URL = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'author_url'
FIELD_COLLECTION_NAME = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'collection'
FIELD_COLLECTION_URL = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'collection_url'
FIELD_TAGS = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'tags'
FIELD_TAG = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'tag'  # Used for filtering a single tag, singular form reads better
FIELD_DESCRIPTION = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'description'
FIELD_TIMESTAMP = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'timestamp'  # Use AUDIOCOMMONS_STRING_TIME_FORMAT (see below)
FIELD_LICENSE = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'license'  # See Licenses section below, should be one of these
FIELD_LICENSE_DEED_URL = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'license_deed_url'
FIELD_IMAGE = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'image'

FIELD_DURATION = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'duration'  # In seconds
FIELD_FORMAT = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'format' # TODO: should he define a list of formats?
FIELD_FILESIZE = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'filesize'  # In bytes
FIELD_CHANNELS = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'channels'  # Integer
FIELD_BITRATE = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'bitrate'  # Integer
FIELD_BITDEPTH = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'bitdepth'  # Integer
FIELD_SAMPLERATE = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'samplerate'  # Integer

FIELD_PREVIEW = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'preview_url'

MINIMUM_RESOURCE_DESCRIPTION_FIELDS = [
    FIELD_ID,
    FIELD_URL,
    FIELD_NAME,
    FIELD_AUTHOR_NAME,
    FIELD_LICENSE,
    FIELD_PREVIEW,
]
ALL_RESOURCE_DESCRIPTION_FIELDS = [globals()[item] for item in dir() if item.startswith('FIELD_')]

# Time format
AUDIOCOMMONS_STRING_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'  # E.g. "2017-09-27 10:01:22"

# Search results parameters
NEXT_PAGE_PROP = 'next'
PREV_PAGE_PROP = 'prev'
NUM_RESULTS_PROP = 'num_results'
RESULTS_LIST = 'results'
# NUM_RESULTS_PROP = 'ac:membersCount'
# RESULTS_LIST = 'ac:collectionAsList'

# Sort options
SORT_OPTION_RELEVANCE = 'relevance'
SORT_OPTION_POPULARITY = 'popularity'
SORT_OPTION_DURATION = 'duration'
SORT_OPTION_DOWNLOADS = 'downloads'
SORT_OPTION_CREATED = 'created'

SORT_OPTIONS = [
    SORT_OPTION_RELEVANCE,
    SORT_OPTION_POPULARITY,
    SORT_OPTION_DURATION,
    SORT_OPTION_DOWNLOADS,
    SORT_OPTION_CREATED,
]

# Licenses
LICENSE_UNKNOWN = 'Unknown'
LICENSE_CC0 = 'CC0'
LICENSE_CC_BY = 'BY'
LICENSE_CC_BY_SA = 'BY-SA'
LICENSE_CC_BY_NC = 'BY-NC'
LICENSE_CC_BY_ND = 'BY-ND'
LICENSE_CC_BY_NC_SA = 'BY-NC-SA'
LICENSE_CC_BY_NC_ND = 'BY-NC-ND'
LICENSE_CC_SAMPLING_PLUS = 'SamplingPlus'
