from ac_mediator.exceptions import ACFieldTranslateException
from services.mixins.constants import MINIMUM_RESOURCE_DESCRIPTION_FIELDS


class BaseACServiceSearch(object):
    """
    Base class for search-related mixins.
    TODO: documentation
    """

    def translate_field(self, ac_field_name, result):
        """
        Given an audio commons field name and a dictionary representing a single result entry form a
        service response, return the corresponding field value compatible with the Audio
        Commons API. To perform this translation first we check if the field is available in
        self.direct_fields_mapping. If that is the case, this function simply returns the corresponding
        value according to the field name mapping specified in self.direct_fields_mapping.
        If field name is not available in self.direct_fields_mapping, then the service object is
        expected to implement a specific method for providing the translation for the field.
        Such method should be named 'translate_field_ACFIELDNAME', where 'ACFIELDNAME' is the name
        of the field as defined in the Audio Commons API (see services.mixins.constants.py).
        We check if this method exists and call it if that's the case (returning its response).
        If method does not exist we raise an exception to inform that field could not be translated.
        :param ac_field_name: name of the field in the Audio Commons API domain
        :param result: dictionary representing a single result entry form a service response
        :return: value of ac_field_name for the given result
        """
        if ac_field_name in self.direct_fields_mapping:
            try:
                return result[self.direct_fields_mapping[ac_field_name]]
            except Exception as e:  # Using generic catch on purpose here to notify in the frontend
                raise ACFieldTranslateException(
                    'Can\'t translate field \'{0}\' ({1}: {2})'.format(ac_field_name, e.__class__.__name__, e))
        get_method_name = 'translate_field_{0}'.format(ac_field_name)
        if get_method_name in dir(self):
            try:
                return getattr(self, get_method_name)(result)
            except Exception as e:  # Using generic catch on purpose here to notify in the frontend
                raise ACFieldTranslateException(
                    'Can\'t translate field \'{0}\' ({1}: {2})'.format(ac_field_name, e.__class__.__name__, e))
        raise ACFieldTranslateException('Can\'t translate field \'{0}\' (unexpected field)'.format(ac_field_name))

    @property
    def direct_fields_mapping(self):
        """
        Return a dictionary of Audio Commons field names that can be directly mapped to
        service resource fields. 'directly mapped' means that the value can be passed
        to the response unchanged and only the field name needs (probably) to be changed.
        For example, id service provider returns a result such as {'original_filename': 'audio filename'},
        we just need to change 'original_filename' for 'name' in order to make it compatible
        with Audio Commons format. Therefore, the direct_fields_mapping dictionary would include
        an entry like 'AUDIO_COMMONS_TERM_FOR_FIELD_NAME': 'original_filename'.
        :return: dictionary mapping (keys are Audio Commons field names and values are services' resource field names)
        """
        return {}

    def translate_single_result(self, result, target_fields=MINIMUM_RESOURCE_DESCRIPTION_FIELDS, fail_silently=False):
        """
        Take an individual search result from a service response in the form of a dictionary
        and translate its keys and values to an Audio Commons API compatible format.
        This method iterates over a given set of target ac_fields and computes the value
        that each field should have in the Audio Commons API context.
        :param result: dictionary representing a single result entry form a service response
        :param target_fields: list of Audio Commons fields to return (default: MINIMUM_RESOURCE_DESCRIPTION_FIELDS)
        :param fail_silently: whether to raise an exception if a particular field can not be translated or use a value of 'None'
        :return: dictionary representing the single result with keys and values comparible with Audio Commons API
        """
        translated_result = dict()
        for ac_field_name in target_fields:
            try:
                trans_field_value = self.translate_field(ac_field_name, result)
            except ACFieldTranslateException as e:
                if not fail_silently:
                    raise e  # Propagate exception
                else:
                    translated_result[ac_field_name] = None
                    print(e)  # Simply print exception message and continue
                continue
            translated_result[ac_field_name] = trans_field_value
        return translated_result

    def format_search_response(self, response):
        """
        Take the search request response returned from the service and transform it
        to the unified Audio Commons search response definition
        :param response: dictionary with json search response
        :return: dictionary with search results properly formatted
        """
        raise NotImplementedError


class ACServiceTextSearch(BaseACServiceSearch):
    """
    Mixin that defines methods to allow text search.
    Services are expected to override methods to adapt them to their own APIs.
    """

    TEXT_SEARCH_ENDPOINT_URL = 'http://example.com/api/search/'

    def text_search(self, query):
        """
        This function takes as input parameters those defined in the Audio Commons API
        specification for text search and translates them to the corresponding parameters
        of the specific service endpoint.
        Then it makes the corresponding request and returns a json response as a dictionary
        if the response status code is 200 or raises an exception otherwise.
        :param query: textual input query
        :return: text search response as dictionary
        """
        # TODO: define which input parameters should text search support (this is part of
        # TODO: api specification). For now we only support 'query' as standard textual query.
        # TODO: calls to methods that trigger calls should be probably logged somewhere...
        raise NotImplementedError
