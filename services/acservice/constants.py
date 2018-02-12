from api.constants import *

# String used to be the base of ACIDs
# Param substitution will be used to provide a service-specific prefix to the id
ACID_SEPARATOR_CHAR = ':'

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

#          "@id": "audioClips:Freesound/385285", "dc:title": "01 - Cars across_city.wav",
#          "dc:description": "Recorded in Moscow. Cars across on street.",
#          "ac:duration": 127.321,
          "ac_isPublishedBy": {
            "@id": "users:Freesound/semenov_nick",
            "foaf:homepage": "https://www.freesound.org/apiv2/users/semenov_nick/"
          },
          "ac:encodesDigitalSignal": {"ac:bitsPerSample": 31, "ac:channels": 2, "ac:sampleRate": 48000.0},
          "ac:availableAs": [
            {
              "@id": "https://freesound.org/data/previews/170/170992_142024-hq.ogg", "@type": "ac:AudioFile",
              "ebu:hasEncodingFormat": "wav", "ebu:bitRate": 3001, "ebu:fileSize": 48915012
            }
          ],
          "ac_isMemberContentOf": "packs:Freesound/21409/",
          "cc:license": "http://creativecommons.org/publicdomain/zero/1.0/",
          "ac:audioCategory": ["fstags:city", "fstags:cars"],
          "ac:homepage": "https://freesound.org/people/semenov_nick/sounds/385285/"


# Resource fields (just using fake names here)
FIELD_ID = '@id'
FIELD_URL = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'url'
FIELD_NAME = 'dc:title'
FIELD_AUTHOR_NAME = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'author'
FIELD_AUTHOR_URL = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'author_url'
FIELD_COLLECTION_NAME = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'collection'
FIELD_COLLECTION_URL = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'collection_url'
FIELD_TAGS = 'ac:audioCategory'
FIELD_TAG = 'ac:audioCategory'  # Used for filtering a single tag, singular form reads better
FIELD_DESCRIPTION = 'dc:description'
FIELD_TIMESTAMP = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'timestamp'  # Use AUDIOCOMMONS_STRING_TIME_FORMAT (see below)
FIELD_LICENSE = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'license'  # See Licenses section below, should be one of these
FIELD_LICENSE_DEED_URL = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'license_deed_url'
FIELD_IMAGE = AUDIOCOMMONS_ONTOLOGY_PREFIX + 'image'

FIELD_DURATION = 'ac:duration'  # xsd:float TODO: Currently in seconds, should be in ms
FIELD_CHANNELS = 'ac:encodesDigitalSignal[1]/ac:channels'  # xsd:nonNegativeInteger
FIELD_BITDEPTH = 'ac:encodesDigitalSignal[1]/ac:bitsPerSample'  # xsd:integer
FIELD_SAMPLERATE_FLOAT = 'ac:encodesDigitalSignal[1]/ac:sampleRate'  # xsd:float

'ac:availableAs[1]/@id'
FIELD_FORMAT = 'ac:availableAs[1]/ebu:hasEncodingFormat' # TODO: should we define a list of formats?
FIELD_FILESIZE = 'ac:availableAs[1]/ebu:filesize'  # In bytes
FIELD_BITRATE = 'ac:availableAs[1]/ebu:audioBitRate'  # xsd:nonNegativeInteger
# "@type": "ac:AudioFile"

FIELD_CHANNELS = FIELD_CHANNELS + '|ac:availableAs[1]/ebu:audioChannelNumber'  # xsd:nonNegativeInteger
FIELD_BITDEPTH = FIELD_BITDEPTH + '|ac:availableAs[1]/ebu:bitDepth'  # xsd:integer
FIELD_SAMPLERATE = 'ac:availableAs[1]/ebu:sampleRate'  # xsd:integer

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
