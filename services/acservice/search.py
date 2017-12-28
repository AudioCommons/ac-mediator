from ac_mediator.exceptions import ACFieldTranslateException, ACException, ACFilterParsingException
from services.acservice.constants import *
from services.acservice.utils import parse_filter
import pyparsing


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


def translates_filter_for_field(field_name):
    """
    TODO: document this function
    """
    def wrapper(func):
        func._translates_filter_for_field_name = field_name
        return func
    return wrapper


class BaseACServiceSearchMixin(object):
    """
    Base class for search-related mixins.
    This class is in charge of providing necessary methods for handling translation of metadata field names
    and values between the 3rd party service and the Audio Commons API and ecosystem. In this way, when
    3rd party service returns a list of results with services particular fields and values, we can translate
    these to a unified Audio Commons format.
    Services that implement any of the search functionalities must at least implement:
        - BaseACServiceSearchMixin.format_search_response(self)
        - BaseACServiceSearchMixin.direct_fields_mapping(self) and/or necessary methods for translating individual
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
        when running self.conf_search() (see BaseACServiceSearchMixin.conf_search(self, *args).
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
        return self.name + ACID_SEPARATOR_CHAR

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

    @translates_filter_for_field(FIELD_ID)
    def translate_filter_id(self, value):
        """
        Default implementation for the translation of ID filter. It uses the provided SERVICE_ID_FIELDNAME as key
        for the filter, and removes self.id_prefix from the start of the filter value. This should operate in reverse
        to what `translate_field_id`. In `translate_field_id` we append a prefix to the third party service provided
        id (e.g. 1234 -> prefix:1234). Here we remove that prefix to convert the value to the original (e.g. prefix:1234
        -> 1234). If a more complex strategy should be followed to filter by FIELD_ID then this function
        must be overwritten.
        :param result: raw value passed to the filter
        :return: tuple with translated (filter_name, filter_value)
        """
        return self.SERVICE_ID_FIELDNAME, value[len(self.id_prefix):]

    def get_supported_fields(self):
        """
        Checks which AudioCommons fields can be translated to the third party service fields.
        These are the fields supported in 'direct_fields_mapping' and those added in the
        'translate_field_methods_registry' using the @translates_field decorator.
        :return: list of available AudioCommons field names
        """
        return list(self.direct_fields_mapping.keys()) + list(self.translate_field_methods_registry.keys())

    def translate_single_result(self, result, target_fields):
        """
        Take an individual search result from a service response in the form of a dictionary
        and translate its keys and values to an Audio Commons API compatible format.
        This method iterates over a given set of target ac_fields and computes the value
        that each field should have in the Audio Commons API context.
        :param result: dictionary representing a single result entry form a service response
        :param target_fields: list of Audio Commons fields to return
        :return: dictionary representing the single result with keys and values compatible with Audio Commons API
        """
        translated_result = dict()
        if target_fields is None:
            target_fields = list()  # Avoid non iterable error
        for ac_field_name in target_fields:
            try:
                trans_field_value = self.translate_field(ac_field_name, result)
            except ACFieldTranslateException as e:
                # Uncomment following line if we want to set field to None if can't be translated
                # translated_result[ac_field_name] = None
                self.add_response_warning("Can't return unsupported field {0}".format(ac_field_name))
                continue
            translated_result[ac_field_name] = trans_field_value
        return translated_result

    def format_search_response(self, response, common_search_params):
        """
        Take the search request response returned from the service and transform it
        to the unified Audio Commons search response definition.

        :param response: dictionary with json search response
        :param common_search_params: common search parameters passed here in case these are needed somewhere
        :return: dictionary with search results properly formatted
        """
        results = list()
        for result in self.get_results_list_from_response(response):
            translated_result = \
                self.translate_single_result(result, target_fields=common_search_params.get('fields', None))
            results.append(translated_result)
        return {
            NUM_RESULTS_PROP: self.get_num_results_from_response(response),
            RESULTS_LIST: results,
        }

    def process_common_search_params(self, common_search_params):
        """
        This method calls all the functions that process common search parameters (i.e. process_x_query_parameter) and
        aggregates their returned query parameters for the third party service request.
        Raise warnings using the BaseACService.add_response_warning method.
        :param common_search_params: common search query parameters as parsed in the corresponding API view
        :return: query parameters dict
        """
        params = dict()

        # Process 'size' query parameter
        size = common_search_params[QUERY_PARAM_SIZE]
        if size is not None:  # size defaults to 15 so it should never be 'None'
            try:
                params.update(self.process_size_query_parameter(size, common_search_params))
            except NotImplementedError as e:
                self.add_response_warning(str(e))

        # Process 'page' query parameter
        page = common_search_params[QUERY_PARAM_PAGE]
        if page is not None:
            try:
                params.update(self.process_page_query_parameter(page, common_search_params))
            except NotImplementedError as e:
                self.add_response_warning(str(e))

        return params

    # ***********************************************************************
    # The methods below are expected to be overwritten by individual services
    # ***********************************************************************

    def get_results_list_from_response(self, response):
        """
        Given the complete response of a search request to the end service, return the list of results.
        :param response: dictionary with the full json response of the request
        :return: list of dict where each dict is a single result
        """
        raise NotImplementedError("Service must implement method BaseACServiceSearchMixin.get_results_list_from_response")

    def get_num_results_from_response(self, response):
        """
        Given the complete response of a search request to the end service, return the total number of results.
        :param response: dictionary with the full json response of the request
        :return: number of total results (integer)
        """
        raise NotImplementedError("Service must implement method BaseACServiceSearchMixin.get_results_list_from_response")

    def process_size_query_parameter(self, size, common_search_params):
        """
        Process 'size' search query parameter and translate it to corresponding query parameter(s)
        for the third party service. Raise warnings using the BaseACService.add_response_warning method.
        The query parameters are returned as a dictionary where keys and values will be sent as keys and values of
        query parameters in the request to the third party service. Typically the returned query parameters dictionary
        will only contain one key/value pair.
        :param size: number of desired results per page (int)
        :param common_search_params: dictionary with other common search query parameters (might not be needed)
        :return: query parameters dict
        """
        raise NotImplementedError("Parameter '{0}' not supported".format(QUERY_PARAM_SIZE))

    def process_page_query_parameter(self, page, common_search_params):
        """
        Process 'page' search query parameter and translate it to corresponding query parameter(s)
        for the third party service. Raise warnings using the BaseACService.add_response_warning method.
        The query parameters are returned as a dictionary where keys and values will be sent as keys and values of
        query parameters in the request to the third party service. Typically the returned query parameters dictionary
        will only contain one key/value pair.
        :param page: requested page number (int)
        :param common_search_params: dictionary with other common search query parameters (might not be needed)
        :return: query parameters dict
        """
        raise NotImplementedError("Parameter '{0}' not supported".format(QUERY_PARAM_PAGE))

    def add_extra_search_query_params(self):
        """
        Return a dictionary with any extra query parameters in key/value pairs that should be added to the
        search request.
        :return: query parameters dict
        """
        return dict()


class ACServiceTextSearchMixin(BaseACServiceSearchMixin):
    """
    Mixin that defines methods to allow text search.
    Services are expected to override methods to adapt them to their own APIs.
    """

    TEXT_SEARCH_ENDPOINT_URL = 'http://example.com/api/search/'

    translate_filter_methods_registry = None

    def conf_textsearch(self, *args):
        """
        Add SEARCH_TEXT_COMPONENT to the list of implemented components.
        Also search for methods in the class that have been annotated with the property
        '_translates_filter_for_field_name'. These will be methods decorated with the 'translates_filter_for_field'
        decorator. Then register methods in self.translate_filter_methods_registry so that these can be accessed later.
        """
        self.implemented_components.append(SEARCH_TEXT_COMPONENT)
        self.translate_filter_methods_registry = dict()
        for method_name in dir(self):
            method = getattr(self, method_name)
            if hasattr(method, '_translates_filter_for_field_name'):
                self.translate_filter_methods_registry[method._translates_filter_for_field_name] = method

    def describe_textsearch(self):
        """
        Returns structured representation of component capabilities
        :return: tuple with (component name, dictionary with component capabilities)
        """
        return SEARCH_TEXT_COMPONENT, {
            SUPPORTED_FIELDS_DESCRIPTION_KEYWORD: self.get_supported_fields(),
            SUPPORTED_FILTERS_DESCRIPTION_KEYWORD: self.get_supported_filters(),
            SUPPORTED_SORT_OPTIONS_DESCRIPTION_KEYWORD: self.get_supported_sorting_criteria(),
        }

    def get_supported_sorting_criteria(self):
        """
        Checks which AudioCommons sorting criteria are supported by the third party service.
        These are the fields that raise an exception when calling 'process_s_query_parameter' with
        'raise_exception_if_unsupported' set to True.
        :return: list of available AudioCommons sorting criteria
        """
        supported_criteria = list()
        for option in SORT_OPTIONS:
            try:
                self.process_s_query_parameter(option, desc=True, raise_exception_if_unsupported=True)
                supported_criteria.append('-{0}'.format(option))
            except ACException:
                pass
            except NotImplementedError:
                # No sorting is supported at all
                return list()

            try:
                self.process_s_query_parameter(option, desc=False, raise_exception_if_unsupported=True)
                supported_criteria.append(option)
            except ACException:
                pass
            except NotImplementedError:
                # No sorting is supported at all
                return list()

        return supported_criteria

    @property
    def direct_filters_mapping(self):
        """
        Return a dictionary of Audio Commons filter names that can be directly mapped to
        service resource filters.
        TODO: complete this documentation
        """
        return {}

    def get_supported_filters(self):
        """
        Checks which AudioCommons filters can be translated to the third party service filters.
        These are the filters defined with the decorator @translates_filter_for_field
        :return: list of available AudioCommons field names (fields equivalent to the filters)
        """
        return list(self.direct_filters_mapping.keys()) + list(self.translate_filter_methods_registry.keys())

    def translate_filter(self, ac_field_name, value):
        """
        TODO: document this
        """
        try:
            if ac_field_name in self.direct_filters_mapping:
                return self.direct_filters_mapping[ac_field_name], value  # Do direct mapping
            return self.translate_filter_methods_registry[ac_field_name](value)  # Invoke translate method
        except KeyError:
            raise ACFilterParsingException('Filter for field \'{0}\' not supported'.format(ac_field_name))
        except ACFilterParsingException:
            raise
        except Exception as e:  # Use generic catch on purpose so we can properly notify the frontend
            raise ACFilterParsingException('Unexpected error processing filter for '
                                           'field \'{0}\' ({1}: {2})'.format(ac_field_name, e.__class__.__name__, e))

    def process_filter_element(self, elm, filter_list):
        """
        TODO: document this function
        :param elm:
        :param filter_list:
        :return:
        """

        def is_filter_term(parse_results):
            return len(parse_results) == 3 and parse_results[1] == ':'

        def is_operator(parse_results):
            return type(parse_results) == str and parse_results.upper() in ['AND', 'OR', 'NOT']

        def is_not_structure(parse_results):
            try:
                return parse_results[0].upper() == 'NOT'
            except Exception:
                return False

        if is_filter_term(elm):
            # If element is a key/value filter pair, render and add it to the filter list
            # Translate key and value for the ones the 3rd party service understands
            fkey = elm[0]
            fvalue = elm[2]
            key, value = self.translate_filter(fkey, fvalue)

            kwargs = {'key': key}
            if type(value) in (int, float):  # Value is number
                kwargs.update({'value_number': value})
            elif type(value) is str:  # Value is text
                kwargs.update({'value_text': value})
            elif type(value) == pyparsing.ParseResults and len(value) == 2:  # Value is a range
                kwargs.update({'value_range': value})
            filter_list.append(self.render_filter_term(**kwargs))

        elif is_operator(elm):
            # If element is an operator, render and add it to the filter list
            filter_list.append(self.render_operator_term(elm))

        elif type(elm) == pyparsing.ParseResults:
            # If element is a more complex structure, walk it recursively and add precedence elements () if needed

            if not is_not_structure(elm):
                filter_list.append('(')
            for item in elm:
                self.process_filter_element(item, filter_list)
            if not is_not_structure(elm):
                filter_list.append(')')
        else:
            raise ACFilterParsingException

    def build_filter_string(self, filter_input_value):
        """
        TODO: document this function
        :param filter_input_value:
        :return:
        """
        try:
            parsed_filter = parse_filter(filter_input_value)
        except pyparsing.ParseException:
            raise ACFilterParsingException('Could not parse filter: "{0}"'.format(filter_input_value))
        out_filter_list = list()
        self.process_filter_element(parsed_filter[0], out_filter_list)
        if out_filter_list[0] == '(':
            # If out filter list starts with an opening parenthesis, remove first and last positions ad both will
            # correspond to redundant parentheses
            out_filter_list = out_filter_list[1: -1]
        filter_string = ''.join(out_filter_list)
        return filter_string

    def text_search(self, context, q, f, s, common_search_params):
        """
        This function a search request to the third party service and returns a formatted json
        response as a dictionary if the response status code is 200 or raises an exception otherwise.

        Note that to implement text search services do not typically need to overwrite this method
        but the individual `process_x_query_parameter` methods.

        During processing of the response a number of warnings can be raised using the
        BaseACService.add_response_warning method. This warnings should contain additional
        relevant information regarding the request/response that will be returned in the aggregated
        response. For example, if a request wants to retrieve a number of metadata fields and one of these
        fields is not supported by the third party service, this will be recorded as a warning.
        We want to return the other supported fields but also a note that says that field X was not
        returned because it is not supported by the service.

        Common search parameters include:
        TODO: write common params when decided

        :param context: Dict with context information for the request (see api.views.get_request_context)
        :param q: textual input query
        :param f: query filter
        :param s: sorting criteria
        :param common_search_params: dictionary with other search parameters commons to all kinds of search
        :return: formatted text search response as dictionary
        """
        query_params = dict()

        # Process 'q' query parameter
        try:
            query_params.update(self.process_q_query_parameter(q))
        except NotImplementedError as e:
            self.add_response_warning(str(e))

        # Process 'f' parameter (if specified)
        if f is not None:
            try:
                query_params.update(self.process_f_query_parameter(f))
            except NotImplementedError as e:
                self.add_response_warning(str(e))

        # Process 's' parameter (if specified)
        if s is not None:
            try:
                desc = False
                if s.startswith('-'):
                    desc = True
                    s = s[1:]
                query_params.update(self.process_s_query_parameter(s, desc))
            except NotImplementedError as e:
                self.add_response_warning(str(e))

        # Process common search parameters
        query_params.update(self.process_common_search_params(common_search_params))

        # Add extra query parameters
        query_params.update(self.add_extra_search_query_params())

        # Send request and process response
        response = self.send_request(self.TEXT_SEARCH_ENDPOINT_URL, params=query_params)
        formatted_response = self.format_search_response(response, common_search_params)
        return formatted_response

    # ***********************************************************************
    # The methods below are expected to be overwritten by individual services
    # ***********************************************************************

    def process_q_query_parameter(self, q):
        """
        Process contents of textual query input parameter and translate it to corresponding query parameter(s)
        for the third party service. Raise warnings using the BaseACService.add_response_warning method.
        The query parameters are returned as a dictionary where keys and values will be sent as keys and values of
        query parameters in the request to the third party service. Typically the returned query parameters dictionary
        will only contain one key/value pair.
        :param q: textual input query
        :return: query parameters dict
        """
        raise NotImplementedError("Parameter '{0}' not supported".format(QUERY_PARAM_QUERY))

    def process_f_query_parameter(self, f):
        """
        Process contents of query filter and translate it to corresponding query parameter(s)
        for the third party service. Raise warnings using the BaseACService.add_response_warning method.
        The query parameters are returned as a dictionary where keys and values will be sent as keys and values of
        query parameters in the request to the third party service. Typically the returned query parameters dictionary
        will only contain one key/value pair.
        :param f: query filter
        :return: query parameters dict
        """
        raise NotImplementedError("Parameter '{0}' not supported".format(QUERY_PARAM_FILTER))

    def process_s_query_parameter(self, s, desc, raise_exception_if_unsupported=False):
        """
        Process contents of sort parameter and translate it to corresponding query parameter(s)
        for the third party service. Raise warnings using the BaseACService.add_response_warning method.
        The query parameters are returned as a dictionary where keys and values will be sent as keys and values of
        query parameters in the request to the third party service. Typically the returned query parameters dictionary
        will only contain one key/value pair.
        :param s: sorting method
        :param desc: use descending order
        :param raise_exception_if_unsupported: whether to raise an exception if desired criteria is unsupported
        :return: query parameters dict
        """
        raise NotImplementedError("Parameter '{0}' not supported".format(QUERY_PARAM_SORT))

    def render_filter_term(self, key, value_text=None, value_number=None, value_range=None):
        """
        TODO: document this function
        :param key:
        :param value_text:
        :param value_number:
        :param value_range:
        :return:
        """
        NotImplementedError("Service must implement method ACServiceTextSearchMixin.render_filter_term "
                            "to support filtering")

    def render_operator_term(self, operator):
        """
        TODO: document this function
        :param key:
        :param value_text:
        :param value_number:
        :param value_range:
        :return:
        """
        NotImplementedError("Service must implement method ACServiceTextSearchMixin.render_operator_term "
                            "to support filtering")
