from services.acservice.constants import LICENSING_COMPONENT


class ACLicensingMixin(object):
    """
    Mixin that defines methods to allow licensing of Audio Commons content.
    Services are expected to override methods to adapt them to their own APIs.
    """
    LICENSING_ACID_DOMAINS = list()

    def conf_licensing(self, conf):
        self.implemented_components.append(LICENSING_COMPONENT)

    def describe_licensing(self):
        """
        Returns structured representation of component capabilities
        Component capabilities include a list of `acid_domains` which indicate for which
        domain of resources the service provides licensing for (i.e., 'Jamendo' domain means all
        resources identified by Jamendo:xxx)
        :return: tuple with (component name, dictionary with component capabilities)
        """
        return LICENSING_COMPONENT, {
            'acid_domains': self.LICENSING_ACID_DOMAINS,
        }

    def get_licensing_url(self, context, acid, *args, **kwargs):
        """
        Given an Audio Commons unique resource identifier (acid), this function returns a url
        where the resource can be licensed. If the 3rd party service can't license that resource or
        some other errors occur during the collection of the url, an AC exceptions should be raised.
        Individual services can extend this method with extra parameters to make it more suitable to their
        needs (e.g., to call the method given an already retrieved resource and avoid in this way an
        extra request).
        :param context: Dict with context information for the request (see api.views.get_request_context)
        :param acid: Audio Commons unique resource identifier
        :return: url to license the input resource (string)
        """
        raise NotImplementedError("Service must implement method ACLicensingMixin.get_licensing_url")

    def license(self, context, acid, *args, **kwargs):
        """
        This endpoint returns a license url along with a list of warnings that might contain relevant
        information for the application. To get the URL, it uses 'get_licensing_url' method, therefore
        'get_licensing_url' is the main method that should be overwritten by third party services.
        Raise warnings using the BaseACService.add_response_warning method.
        :param context: Dict with context information for the request (see api.views.get_request_context)
        :param acid: Audio Commons unique resource identifier
        :return: url where to get a license
        """
        return {'license_url': self.get_licensing_url(context, acid, *args, **kwargs)}
