from ac_mediator.exceptions import UnexpectedServiceResourceField


class BaseACServiceSearch(object):
    """
    Base class for search-related mixins.
    TODO: documentation
    """

    def translate_field(self, service_field_name, service_field_value):
        """
        Given a resource field and its value, return the translated version of it which
        is compatible with the Audio Commons API.
        To perform this translation first we check if the field is available in self.direct_fields_mapping.
        If that is the case, this function just translates the field name and returns the translated
        (field_name, field_value) tuple.
        If field name is not available in self.direct_fields_mapping, then the object should implement
        a specific method for providing the translation for the field. Such method should be named
        'translate_field_FIELDNAME'. We check if this method exists and call it if that's the case (returning
        its response). If method does not exist we raise an exception to inform that field could not be
        translated.
        :param service_field_name: name of the field
        :param service_field_value: value of the field
        :return: tuple with (translated field name, translated field value)
        """
        if service_field_name in self.direct_fields_mapping:
            return self.direct_fields_mapping[service_field_name], service_field_value
        get_method_name = 'translate_field_{0}'.format(service_field_name)
        if get_method_name in dir(self):
            return getattr(self, get_method_name)(service_field_value)
        raise UnexpectedServiceResourceField('Can\'t translate unexpected field {0}'.format(service_field_name))

    @property
    def direct_fields_mapping(self):
        """
        Return a dictionary of service resource fields that can be directly mapped to
        Audio Commons fields. 'directly mapped' means that the value can be passed
        to the response unchanged and only the field name needs (probably) to be changed.
        For example, id service provider returns something like {'original_filename': 'audio filename'},
        we just need to change 'original_filename' for 'name' in order to make it compatible
        with Audio Commons format.
        :return: dictionary mapping (keys are services resource field names and values are Audio Commons field names)
        """
        raise NotImplementedError

    def translate_single_result(self, result, fail_silently=False):
        translated_result = dict()
        for field_name, field_value in result.items():
            try:
                trans_field_name, trans_field_value = self.translate_field(field_name, field_value)
            except UnexpectedServiceResourceField as e:
                if not fail_silently:
                    raise e  # Propagate exception
                continue
            translated_result[trans_field_name] = trans_field_value
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
