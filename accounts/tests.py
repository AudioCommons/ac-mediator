from django.test import TestCase, override_settings
from accounts.models import Account
from django.core.urlresolvers import reverse
from django.core import mail
from django.conf import settings


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class AccountRegistrationTestCase(TestCase):

    def test_user_registration(self):

        # Register new account
        post_data = {
            'password1': '123456',
            'password2': '123456',
            'accepted_tos': 'on',
            'username': 'test_username',
            'email1': 'example@email.com',
            'email2': 'example@email.com',
        }
        resp = self.client.post(reverse('registration'), data=post_data)
        self.assertEquals(resp.status_code, 200)

        # Check that a user object has been created with that user name but it is still inactive
        account = Account.objects.get(username='test_username')
        self.assertEquals(account.is_active, False)

        # Check that an email was sent
        self.assertEquals(len(mail.outbox), 1)

        # Try to activate user with wrong username
        resp = self.client.get(reverse('accounts-activate', args=['fake_username', 'fake_hash']))
        self.assertEquals(resp.status_code, 200)
        self.assertEquals('the user you are trying to activate does not exist' in resp.content.decode("utf-8"), True)

        # Try to activate user with fake hash
        resp = self.client.get(reverse('accounts-activate', args=[account.username, 'fake_hash']))
        self.assertEquals(resp.status_code, 200)
        self.assertEquals("we can't find that activation key" in resp.content.decode("utf-8"), True)

        # Extract hash from email and activate user
        email_body = mail.outbox[0].body
        activation_url = [line for line in email_body.split('\n') if line.startswith(settings.BASE_URL)][0]
        uid_hash = activation_url.split('/')[-2]
        resp = self.client.get(reverse('accounts-activate', args=[account.username, uid_hash]))
        self.assertEquals(resp.status_code, 200)
        self.assertEquals('Activation succeeded...' in resp.content.decode("utf-8"), True)

        # Check that user is now active
        account = Account.objects.get(username='test_username')
        self.assertEquals(account.is_active, True)
