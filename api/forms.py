from django import forms
from django.forms import ModelForm
from django.forms.fields import Field
from api.models import ApiClient
setattr(Field, 'is_checkbox', lambda self: isinstance(self.widget, forms.CheckboxInput))  # Used in the template


class ApiClientForm(ModelForm):
    class Meta:
        model = ApiClient
        fields = ['name', 'agree_tos']
        labels = {
            'name': 'Name of your application',
            'agree_tos': 'Terms of service',
        }
        help_texts = {
            'agree_tos': 'I agree with the Audio Commons API terms of service',
        }

    def clean_agree_tos(self):
        agree_tos = self.cleaned_data['agree_tos']
        if not agree_tos:
            raise forms.ValidationError("To use the Audio Commons API you must agree with the terms of service")
        return agree_tos
