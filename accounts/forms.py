from django import forms
from accounts.models import Account
from django.utils.translation import ugettext as _


class RegistrationForm(forms.Form):
    username = forms.RegexField(
        label=_("Username"),
        min_length=3,
        max_length=30,
        regex=r'^\w+$',
        help_text=_("Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores)."),
        error_messages={'only_letters': _("This value must contain only letters, numbers and underscores.")}
    )
    first_name = forms.CharField(help_text=_("Optional."), max_length=30, required=False)
    last_name = forms.CharField(help_text=_("Optional."), max_length=30, required=False)
    email1 = forms.EmailField(label=_("Email"), help_text=_("We will send you a confirmation/activation email, so make "
                                                            "sure this is correct!."))
    email2 = forms.EmailField(label=_("Email confirmation"))
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)
    accepted_tos = forms.BooleanField(
        label='',
        help_text=_('Check this box to accept the <a href="###" target="_blank">terms of use</a>'),
        required=True,
        error_messages={'required': _('You must accept the terms of use in order to register.')}
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            Account.objects.get(username__iexact=username)
        except Account.DoesNotExist:
            return username
        raise forms.ValidationError(_("A user with that username already exists."))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def clean_email2(self):
        email1 = self.cleaned_data.get("email1", "")
        email2 = self.cleaned_data["email2"]
        if email1 != email2:
            raise forms.ValidationError(_("The two email fields didn't match."))
        try:
            Account.objects.get(email__iexact=email2)
            raise forms.ValidationError(_("A user using that email address already exists."))
        except Account.DoesNotExist:
            pass
        return email2

    def save(self):
        username = self.cleaned_data["username"]
        email = self.cleaned_data["email2"]
        password = self.cleaned_data["password2"]
        first_name = self.cleaned_data.get("first_name", "")
        last_name = self.cleaned_data.get("last_name", "")
        accepted_tos = self.cleaned_data.get("accepted_tos", False)

        account = Account(username=username,
                          first_name=first_name,
                          last_name=last_name,
                          email=email,
                          accepted_tos=accepted_tos)
        account.set_password(password)
        account.save()
        return account


class ReactivationForm(forms.Form):
    account = forms.CharField(label="The username or email you signed up with")

    def clean_account(self):
        username_or_email = self.cleaned_data["account"]
        try:
            return Account.objects.get(email__iexact=username_or_email, is_active=False)
        except Account.DoesNotExist:
            pass
        try:
            return Account.objects.get(username__iexact=username_or_email, is_active=False)
        except Account.DoesNotExist:
            pass
        raise forms.ValidationError(_("No non-active user with such email or username exists."))
