from django import forms
from django.forms import ModelForm
from django.forms.fields import Field
from api.models import ApiClient
from oauth2_provider.models import AbstractApplication
from django.utils.translation import ugettext_lazy as _
setattr(Field, 'is_checkbox', lambda self: isinstance(self.widget, forms.CheckboxInput))  # Used in the template


class ApiClientForm(ModelForm):

    # Limit choices available for grant types
    ALLOWED_GRANT_TYPES = (
        (AbstractApplication.GRANT_AUTHORIZATION_CODE, _('Three-legged')),
        (AbstractApplication.GRANT_PASSWORD, _('User and password')),
    )
    authorization_grant_type = forms.ChoiceField(choices=ALLOWED_GRANT_TYPES)

    class Meta:
        model = ApiClient
        fields = ['name', 'agree_tos', 'authorization_grant_type', 'redirect_uris']
        labels = {
            'name': 'Name of your application',
            'agree_tos': 'Terms of service',
            'redirect_uris': 'Redirect URIs',
        }
        help_texts = {
            'agree_tos': 'I agree with the Audio Commons API terms of service',
            'redirect_uris': 'URIs allowed for the OAuth2 redirect step '
                             '(only required for Three-legged authorization grant type). '
                             'Separate URIs using spaces.',
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if not name.strip():
            raise forms.ValidationError("This field is required")
        return name

    def clean_agree_tos(self):
        agree_tos = self.cleaned_data['agree_tos']
        if not agree_tos:
            raise forms.ValidationError("To use the Audio Commons API you must agree with the terms of service")
        return agree_tos

    def clean_redirect_uris(self):
        redirect_uris = self.cleaned_data['redirect_uris']
        if not redirect_uris \
                and self.cleaned_data['authorization_grant_type'] == AbstractApplication.GRANT_AUTHORIZATION_CODE:
            raise forms.ValidationError(_('This field is required when using Three-legged authorization grant'))
        return redirect_uris
