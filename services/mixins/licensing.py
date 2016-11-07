from services.mixins.constants import LICENSING_COMPONENT


class ACLicensingMixin(object):
    """
    Mixin that defines methods to allow licensing of Audio Commons content.
    Services are expected to override methods to adapt them to their own APIs.
    """

    def conf_licensing(self, conf):
        self.implemented_components.append(LICENSING_COMPONENT)

    def get_licensing_url(self, *args, **kwargs):
        """
        Given some input data about a specific resource, this functionr returns the url where the
        resource can be licensed.
        :return: url to license the input resource
        """
        # TODO: this is just a proposal of how licensing service could be handled
        raise NotImplementedError("Service must implement method ACLicensingMixin.get_licensing_url")
