from services.acservice.constants import LICENSING_COMPONENT


class ACLicensingMixin(object):
    """
    Mixin that defines methods to allow licensing of Audio Commons content.
    Services are expected to override methods to adapt them to their own APIs.
    """

    def conf_licensing(self, conf):
        self.implemented_components.append(LICENSING_COMPONENT)

    def get_licensing_url(self, acid, *args, **kwargs):
        """
        Given an Audio Commons unique resource identifier (acid), this function returns a url
        where the resource can be licensed. If the 3rd party service can't license that resource or
        some other errors occur during the collection of the url, an ACLicesningException should be raised.
        Individual services can extend this method with extra parameters to make it more suitable to their
        needs (e.g., to call the method given an already retrieved resource and avoid in this way an
        extra request).
        :return: url to license the input resource (string)
        """
        raise NotImplementedError("Service must implement method ACLicensingMixin.get_licensing_url")

    def license(self, acid, *args, **kwargs):
        """
        This endpoint returns a license url along with a list of warnings that might contain relevant
        information for the application. To get the URL, it uses 'get_licensing_url' method, therefore
        'get_licensing_url' is the main method that should be overwritten by third party services.
        Raise warnings using the BaseACService.add_response_warning method.
        :param acid: Audio Commons unique resource identifier
        :return: url where to get a license
        """
        return {'license_url': self.get_licensing_url(acid, *args, **kwargs)}
