from django.db import models
from django.core.urlresolvers import reverse
from oauth2_provider.models import AbstractApplication


class ApiClient(AbstractApplication):
    """
    This is our custom 'Application' model for Oauth authentication.
    """

    agree_tos = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    #  Add more custom fields here like description, logo, preferred services...

    def get_absolute_url(self):
        return reverse('developers-app-detail', args=[self.id])

    def save(self, *args, **kwargs):
        """
        We override save method so we can set `authorization_grant_type` and `client_type`
        to default values. Current API clients can only use the password grant authorization
        type, therefore these fields are not included in the API client form and we need
        to set them automatically. In the future if we allow other authorization types such as
        the code grant and let users choose then this won't be necessary.
        """
        if not self.authorization_grant_type:
            self.authorization_grant_type = AbstractApplication.GRANT_PASSWORD
        super(ApiClient, self).save(*args, **kwargs)
