from django.db import models
from django.urls import reverse
from oauth2_provider.models import AbstractApplication


class ApiClient(AbstractApplication):
    """
    This is our custom 'Application' model for Oauth authentication.
    """

    agree_tos = models.BooleanField(default=False)
    password_grant_is_allowed = models.BooleanField(default=False)  # Enable password grant in OAuth2 authentication
    created = models.DateTimeField(auto_now_add=True)
    #  Add more custom fields here like description, logo, preferred services...

    def get_absolute_url(self):
        return reverse('developers:app-detail', args=[self.id])

    def clean(self):
        """
        The AbstractApplication model includes a clean method that raises a ValidationError
        if the redirect_uri is empty and is required by the authorization_grant_type. We have
        implemented a custom version of this check (with a custom message) in api.forms.ApiClientForm
        therefore we don't need model's clean method to do anything.
        """
        pass
