from django.core.management.base import BaseCommand
from django.conf import settings
from api.response_aggregator import get_response_aggregator
import datetime
import logging


logger = logging.getLogger('management')


class Command(BaseCommand):
    help = 'Clean response objects in the store which are older than `N` days.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        """
        Every time a new request is made to the endpoints of the Audio Commons API (e.g. search), a response 
        dictionary is created and stored in a shared key-value store (we use a Redis backend). This 
        dictionary is updated as soon as new responses from 3rd party services are received and can be 
        consumed by clients using the /collect endpoint of the Audio Commons API. 
        
        To avoid collapsing our store with unneeded response objects, this commands deletes response objects 
        which are older than a particular number of days. It should be run periodically.
        
        More info: https://github.com/AudioCommons/ac-mediator/issues/8
        """

        n_deleted_responses = 0
        n_responses = 0
        response_aggregator = get_response_aggregator()
        store = response_aggregator.store

        for key in store.get_all_response_keys():
            response = store.get_response(key)
            if response:
                try:
                    timestamp = datetime.datetime.strptime(response['meta']['sent_timestamp'], '%Y-%m-%d %H:%M:%S.%f')
                    n_responses += 1
                    if (datetime.datetime.now() - timestamp).total_seconds() > settings.RESPONSE_EXPIRY_TIME:
                        store.delete_response(key)
                        n_deleted_responses += 1

                except KeyError:
                    # If object has no timestamp information, continue with the next response
                    # This could be because the object does not really correspond to an API response
                    pass

        logger.info('Removed {0} responses from store (currently has {1} responses)'
                    .format(n_deleted_responses, n_responses - n_deleted_responses))
