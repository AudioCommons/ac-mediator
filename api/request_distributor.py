from ac_mediator.exceptions import ACException
from services.management import get_available_services, get_service_by_id
from api.response_aggregator import get_response_aggregator
from celery import shared_task

response_aggregator = get_response_aggregator()


@shared_task
def perform_request_and_aggregate(request, response_id, service_id):
    service = get_service_by_id(service_id)
    try:
        print('Requesting response from {0} ({1})'.format(service.name, response_id))
        service_response = getattr(service, request['method'])(**request['kwargs'])
        response_aggregator.aggregate_response(response_id, service.name, service_response)
    except ACException as e:
        # Aggregate error response in response aggregator and continue with next service
        response_aggregator.aggregate_response(response_id, service.name, e)


class RequestDistributor(object):

    @staticmethod
    def process_request(request, wait_until_complete=False):
        """
        Process incoming request, and propagate it to corresponding services.
        Requests to 3rd party services are made asynchronously. We send requests to all 3rd
        party services and as soon as a response is received it is added to a response object
        which aggregates the responses from all services.
        In the normal functioaning mode (wait_until_complete=False) this method will immediately
        return a response right after all requests have been sent. This response will mainly
        include a response_id parameter that can be later used to pull the actual responses
        from the 3rd party services (see ResponseAggregator.collect_response).
        If wait_until_complete is set to False, then this method will wait untill a response is
        received for all requests and only then will return an aggregated response including the
        contents of all 3rd party services individual responses.

        :param request: incoming request object
        :param wait_until_complete: whether to return immediately after all requests are sent or wait untill all responses are received
        :return: dictionary with response (as returned by ResponseAggregator.collect_response)
        """

        # Get available services for the given component (e.g. services that do `text search')
        services = get_available_services(component=request['component'])

        # Create object to store responses from services
        response_id = response_aggregator.create_response(len(services))
        response_aggregator.set_response_to_processing(response_id)

        # Iterate over services, perform requests and aggregate responses
        async_response_objects = list()
        for service in services:
            # Requests are performed asynchronously in Celery workers
            async_response_objects.append(
                perform_request_and_aggregate.delay(request, response_id, service.id)
            )

        # Wait until all responses are received (only if wait_until_complete == True)
        if wait_until_complete:
            # We wait until we get a response for all the requests we sent
            # We do that by continuously iterating over all async_response_objetcs in a while
            # loop and only exit when all of them have been flagged as ready
            # TODO: we should add some control over timeouts, etc as this operation is blocking
            while True:
                if all([item.ready() for item in async_response_objects]):
                    break

        # Return object including responses received so far (if wait_until_complete == False the
        # response returned here will almost only contain the response_id field which can be later
        # used to retreive further responses.
        return response_aggregator.collect_response(response_id)


request_distributor = RequestDistributor()

def get_request_distributor():
    return request_distributor
