from ac_mediator.exceptions import ACFieldTranslateException
from services.acservice.constants import MINIMUM_RESOURCE_DESCRIPTION_FIELDS, FIELD_ID, SEARCH_TEXT_COMPONENT


def translates_field(field_name):
    """
    This decorator annotates the decorated function with a '_translates_field_name' property
    with a reference to an Audio Commons metadata field name.
    :param field_name: Audio Commons metadata field name (see services.mixins.constants.py)
    :return: decorated function
    """
    def wrapper(func):
        func._translates_field_name = field_name
        return func
    return wrapper


class BaseACServiceSearch(object):
    """
    Base class for search-related mixins.
    This class is in charge of providing necessary methods for handling translation of metadata field names
    and values between the 3rd party service and the Audio Commons API and ecosystem. In this way, when
    3rd party service returns a list of results with services particular fields and values, we can translate
    these to a unified Audio Commons format.
    Services that implement any of the search functionalities must at least implement:
        - BaseACServiceSearch.format_search_response(self)
        - BaseACServiceSearch.direct_fields_mapping(self) and/or necessary methods for translating individual
          fields using the 'translates_field' decorator
    """

    SERVICE_ID_FIELDNAME = 'id'
    translate_field_methods_registry = None

    def conf_search(self, *args):
        """
        Search for methods in the class that have been annotated with the property '_translates_field_name'.
        These will be methods decorated with the 'translates_field' decorator. Then register methods
        in self.translate_field_methods_registry so that these can be accessed later.
        """
        self.translate_field_methods_registry = dict()
        for method_name in dir(self):
            method = getattr(self, method_name)
            if hasattr(method, '_translates_field_name'):
                self.translate_field_methods_registry[method._translates_field_name] = method

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

    def translate_field(self, ac_field_name, result):
        """
        Given an audio commons field name and a dictionary representing a single result entry form a
        service response, return the corresponding field value compatible with the Audio
        Commons API. To perform this translation first we check if the field is available in
        self.direct_fields_mapping. If that is the case, this function simply returns the corresponding
        value according to the field name mapping specified in self.direct_fields_mapping.
        If field name is not available in self.direct_fields_mapping, then we check if it is available
        in the registry of translate field methods self.translate_field_methods_registry which is built
        when running self.conf_search() (see BaseACServiceSearch.conf_search(self, *args).
        If a method for the ac_field_name exists in self.translate_field_methods_registry we call it and
        return its response.
        If field does not exist in self.direct_fields_mapping or self.translate_field_methods_registry
        we raise an exception to inform that field could not be translated.
        :param ac_field_name: name of the field in the Audio Commons API domain
        :param result: dictionary representing a single result entry form a service response
        :return: value of ac_field_name for the given result
        """
        try:
            if ac_field_name in self.direct_fields_mapping:
                return result[self.direct_fields_mapping[ac_field_name]]  # Do direct mapping
            if ac_field_name in self.translate_field_methods_registry:
                return self.translate_field_methods_registry[ac_field_name](result)  # Invoke translate method
        except Exception as e:  # Use generic catch on purpose so we can properly notify the frontend
            raise ACFieldTranslateException(
                    'Can\'t translate field \'{0}\' ({1}: {2})'.format(ac_field_name, e.__class__.__name__, e))
        raise ACFieldTranslateException('Can\'t translate field \'{0}\' (unexpected field)'.format(ac_field_name))

    @property
    def id_prefix(self):
        return '{0}:'.format(self.name)

    @translates_field(FIELD_ID)
    def translate_field_id(self, result):
        """
        Default implementation for the translation of ID field. It takes the id of the resource
        coming from the service and appends the service name. The id of the resource is taken using the
        SERVICE_ID_FIELDNAME which defaults to 'id'. If this is not the way in which id is provided by the
        service then either SERVICE_ID_FIELDNAME is assigned a different value or this function
        must be overwritten.
        :param result: dictionary representing a single result entry form a service response
        :return: id to uniquely identify resource within the Audio Commons Ecosystem
        """
        return '{0}{1}'.format(self.id_prefix, result[self.SERVICE_ID_FIELDNAME])

    def get_supported_fields(self):
        """
        Checks which AudioCommons fields can be translated to the third party service fields.
        These are the fields supported in 'direct_fields_mapping' and those added in the
        'translate_field_methods_registry' using the @translates_field decorator.
        :return: list of available AudioCommons field names
        """
        return list(self.direct_fields_mapping.keys()) + list(self.translate_field_methods_registry.keys())

    def translate_single_result(self, result, target_fields, fail_silently=False):
        """
        Take an individual search result from a service response in the form of a dictionary
        and translate its keys and values to an Audio Commons API compatible format.
        This method iterates over a given set of target ac_fields and computes the value
        that each field should have in the Audio Commons API context.
        :param result: dictionary representing a single result entry form a service response
        :param target_fields: list of Audio Commons fields to return
        :param fail_silently: whether to raise an exception if a particular field can not be translated or use a value of 'None'
        :return: dictionary representing the single result with keys and values compatible with Audio Commons API
        """
        translated_result = dict()
        if target_fields is None:
            target_fields = list()  # Avoid non iterable error
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

    def format_search_response(self, response, common_search_params):
        """
        Take the search request response returned from the service and transform it
        to the unified Audio Commons search response definition
        :param response: dictionary with json search response
        :param common_search_params: common search parameters passed here in case these are needed somewhere
        :return: dictionary with search results properly formatted
        """
        raise NotImplementedError("Service must implement method BaseACServiceSearch.format_search_response")


class ACServiceTextSearch(BaseACServiceSearch):
    """
    Mixin that defines methods to allow text search.
    Services are expected to override methods to adapt them to their own APIs.
    """

    TEXT_SEARCH_ENDPOINT_URL = 'http://example.com/api/search/'

    def conf_textsearch(self, *args):
        self.implemented_components.append(SEARCH_TEXT_COMPONENT)

    def describe_textsearch(self):
        """
        Returns structured representation of component capabilities
        :return: tuple with (component name, dictionary with component capabilities)
        """
        return SEARCH_TEXT_COMPONENT, {
            'supported_fields': self.get_supported_fields(),
        }

    def text_search(self, q, common_search_params):
        """
        This function takes as input parameters those defined in the Audio Commons API
        specification for text search and translates them to the corresponding parameters
        of the specific service endpoint.
        Then it makes the corresponding request and returns a json response as a dictionary
        if the response status code is 200 or raises an exception otherwise.

        Common search parameters include:
        TODO: write common params when decided

        :param q: textual input query
        :param common_search_params: dictionary with other search parameters commons to all kinds of search
        :return: text search response as dictionary
        """
        raise NotImplementedError("Service must implement method ACServiceTextSearch.text_search")
