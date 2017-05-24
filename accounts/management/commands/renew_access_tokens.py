from django.core.management.base import BaseCommand
from accounts.models import ServiceCredentials
from services.management import get_service_by_id
from ac_mediator.exceptions import ACServiceDoesNotExist
import logging


class Command(BaseCommand):
    help = 'Renew access tokens to 3rd party services whose refresh tokens are about to expire. ' \
           'Use as `python manage.py renew_access_tokens`.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        """
        When users link their accounts with third party services, these typically return an access token
        together with a refresh token. Both types of tokens do expire at some point (refresh tokens have
        a longer lifetime). If the access token expires but the refresh token is still valid, the Audio Commons
        mediator can easily get a renewed pair using the refresh token. However if the refresh token expires,
        then there is no way the mediator can renew the token without user intervention and the user will need to
        manually link his account again.
        
        This account will iterate over user accounts and their linked services, and renew access/refresh token
        pairs in the cases when refresh token is about to expire.
        
        More info: https://github.com/AudioCommons/ac-mediator/issues/4
        """

        n_success = 0
        n_failed = 0

        for service_credentials in ServiceCredentials.objects.all():
            try:
                service = get_service_by_id(service_credentials.service_id)
            except ACServiceDoesNotExist:
                n_failed += 1
                continue  # If service does not exist, don't try to renew credentials

            if service.check_credentials_should_be_renewed_background(service_credentials.credentials)
                success, received_credentials = service.renew_credentials(service_credentials.credentials)
                if success:
                    # Store credentials (replace existing ones if needed)
                    service_credentials, is_new = ServiceCredentials.objects.get_or_create(
                        account=service_credentials.account, service_id=service.id)
                    service_credentials.credentials = received_credentials
                    service_credentials.save()
                    n_success += 1
                else:
                    # If credentials can't be renewed, then users will need to renew them manually
                    n_failed += 1

        logging.info('Renewed {0} service credentials ({0} failed renewal)'.format(n_success, n_failed))
