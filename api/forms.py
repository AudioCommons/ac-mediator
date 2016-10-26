from django.forms import ModelForm
from api.models import ApiClient


class ApiClientForm(ModelForm):
    class Meta:
        model = ApiClient
        fields = ['name', 'agree_tos', 'client_id', 'client_secret', 'client_type', 'authorization_grant_type', 'redirect_uris']
