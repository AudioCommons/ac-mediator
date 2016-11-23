from ac_mediator.exceptions import ACException
from services.management import get_available_services, get_service_by_id
from api.response_aggregator import get_response_aggregator
from celery import shared_task

response_aggregator = get_response_aggregator()


@shared_task
def get_service_response_and_aggregate(request, response_id, service_id):
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
    def process_request(request, async):
        """
        Process incoming request, and propagate it to corresponding services.
        Requests to 3rd party services can be done synchornously or asynchronously.
        When done synchronously this function will be blocking and won't return anything until
        responses are obtained from all services (this is not desired). In other words, when running
        synchronously this function will call every service sequentially and add the results to
        the created response object. Once all have finished, the response status will be set to
        finished and the aggregated contents of the response returned.
        When running requests asynchronously this function will make all requests and return a
        response before waiting for the requests to finish. The returned response will therefore be
        almost empty, but will include a response id field that can be used later in the response
        aggregator to pull the (complete or partial) responses returned from services.

        :param request: incoming request
        :param async: whether to perform asynchronous requests
        :return: response dictionary (with no content from responses with async is on)
        """

        services = get_available_services(component=request['component'])
        # Create object to store response contents
        response_id = response_aggregator.create_response(len(services))
        response_aggregator.set_response_to_processing(response_id)
        # Iterate over services and perform queries
        async_response_refs = list()
        for service in services:
            if async:
                get_service_response_and_aggregate.delay(request, response_id, service.id)
            else:
                async_response_refs.append(
                    get_service_response_and_aggregate.delay(request, response_id, service.id)
                )
        if not async:
            # TODO: document this and update docstrings above
            all_done = False
            while not all_done:
                all_done = True
                for async_response_ref in async_response_refs:
                    if not async_response_ref.ready():
                        all_done = False
                        break
        # Return current results (will be empty in async mode)
        return response_aggregator.collect_response(response_id)


request_distributor = RequestDistributor()

def get_request_distributor():
    return request_distributor
