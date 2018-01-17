from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _
from utils.mail import send_mail
from utils.encryption import create_hash


class Account(AbstractUser):
    """
    This is our custom 'User' model.
    """

    is_developer = models.BooleanField(default=False, blank=False)
    accepted_tos = models.BooleanField(default=False, blank=False)
    #  Add more custom fields here like avatar...

    def send_activation_email(self):
        tvars = {
            'user': self,
            'username': self.username,
            'hash': create_hash(self.id)
        }
        send_mail(self.email, subject='Activate your Audio Commons user account',
                  template='emails/account_activation.txt', context=tvars)

    class Meta:
        verbose_name = _('account')
        verbose_name_plural = _('accounts')


class ServiceCredentials(models.Model):
    """
    This model is intended to store the credentials returned by a service after
    an Audio Commons account is linked with it. Credentials are intentionally
    stored in a JSONField to accommodate different types of credentials returned
    by services. The ACServiceBase authentication methods will be in charge of
    interpreting the contests of the 'credentials' field.
    """

    account = models.ForeignKey(Account, related_name='service_credentials')
    service_id = models.CharField(max_length=64)
    credentials = JSONField(null=False, default={})
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('service credentials')
        verbose_name_plural = _('service credentials')
        unique_together = (('account', 'service_id'),)

    def __str__(self):
        return 'ServiceCredentials for {0} and {1}'.format(self.account.username, self.service_id)
