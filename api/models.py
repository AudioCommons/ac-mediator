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
