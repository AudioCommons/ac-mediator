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
        :return: url to license the input resource
        """
        # TODO: this is just a proposal of how licensing service could be handled
        raise NotImplementedError("Service must implement method ACLicensingMixin.get_licensing_url")
