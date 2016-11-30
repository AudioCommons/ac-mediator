from django import forms
from django.forms import ModelForm
from django.forms.fields import Field
from django.utils.text import mark_safe
from django.forms.widgets import HiddenInput
from api.models import ApiClient
setattr(Field, 'is_checkbox', lambda self: isinstance(self.widget, forms.CheckboxInput))  # Used in the template


class ApiClientForm(ModelForm):

    # We define a number of predefined combinations of client type and authorization grant type
    # from which developers can choose when registering a new API client
    PUBLIC_IMPLICIT = 'public_implicit'
    PUBLIC_PASSWORD = 'public_password'
    CONFIDENTIAL_AUTHORIZATION_CODE = 'confidential_authorization-code'
    APPLICATION_TYPES = (
        (PUBLIC_IMPLICIT, 'Public client with implicit grant'),
        (CONFIDENTIAL_AUTHORIZATION_CODE, 'Confidential client with authorization code grant'),
        (PUBLIC_PASSWORD, 'Public client with password grant'),
    )
    application_type = forms.ChoiceField(
        choices=APPLICATION_TYPES,
        help_text=mark_safe('Please read the documentation on '
                            '<a href="/docs/api_authentication.html" target="_blank">'
                            'choosing the application type</a> before selecting an option.'),
    )

    class Meta:
        model = ApiClient
        fields = ['name', 'agree_tos', 'application_type', 'authorization_grant_type', 'client_type', 'redirect_uris']
        labels = {
            'name': 'Name of your application',
            'agree_tos': 'Terms of service',
            'redirect_uris': 'Redirect URIs',
        }
        help_texts = {
            'agree_tos': 'I agree with the Audio Commons API terms of service',
            'redirect_uris': mark_safe('URIs allowed for the OAuth2 redirect step ' +
                                       '(not required for password grant). ' +
                                       '<br>Separate URIs using spaces.'),
        }
        widgets = {
            'authorization_grant_type': HiddenInput(),
            'client_type': HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set authorization_grant_type and client_type to not required (we automatically fill them at clean time)
        self.fields['authorization_grant_type'].required = False
        self.fields['client_type'].required = False

        # Preload application_type if authorization_grant_type and client_type are set (i.e. when editing application)
        instance = kwargs.get('instance', None)
        if instance:
            application_type = '{0}_{1}'.format(instance.client_type, instance.authorization_grant_type)
            self.initial['application_type'] = application_type

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
        application_type = self.cleaned_data['application_type']
        if not redirect_uris \
                and application_type in (self.PUBLIC_IMPLICIT, self.CONFIDENTIAL_AUTHORIZATION_CODE):
            raise forms.ValidationError('This field is required when using implicit or authorization code grants')
        return redirect_uris

    def clean_authorization_grant_type(self):
        # Set authorization grant time according to application_type
        application_type = self.cleaned_data['application_type']
        if ApiClient.GRANT_IMPLICIT in application_type:
            authorization_grant_type = ApiClient.GRANT_IMPLICIT
        elif ApiClient.GRANT_AUTHORIZATION_CODE in application_type:
            authorization_grant_type = ApiClient.GRANT_AUTHORIZATION_CODE
        elif ApiClient.GRANT_PASSWORD in application_type:
            authorization_grant_type = ApiClient.GRANT_PASSWORD
        else:
            authorization_grant_type = ApiClient.GRANT_IMPLICIT  # Use implicit by default
        self.cleaned_data['authorization_grant_type'] = authorization_grant_type
        return authorization_grant_type

    def clean_client_type(self):
        # Set authorization grant time according to application_type
        application_type = self.cleaned_data['application_type']
        if ApiClient.CLIENT_PUBLIC in application_type:
            client_type = ApiClient.CLIENT_PUBLIC
        else:
            client_type = ApiClient.CLIENT_CONFIDENTIAL
        self.cleaned_data['client_type'] = client_type
        return client_type
