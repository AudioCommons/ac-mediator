from ac_mediator.exceptions import ACException
from services.management import get_available_services
from api.response_aggregator import get_response_aggregator


response_aggregator = get_response_aggregator()


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
        When running requests asynchronously this function will simply return a response id
        as soon as requests have been sent. This response id can be used later in the response
        aggregator to pull the (complete or partial) responses returned from services.

        :param request: incoming request
        :param async: whether to perform asynchronous requests
        :return:
        """

        services = get_available_services(component=request['component'])
        # Create object to store response contents
        response_id = response_aggregator.create_response(len(services))
        response_aggregator.set_response_to_processing(response_id)

        for service in services:
            if not async:
                # Query each service and aggregate results from each service
                try:
                    service_response = getattr(service, request['method'])(**request['kwargs'])
                except ACException as e:
                    # Aggregate error response in response aggregator and continue with next service
                    response_aggregator.aggregate_response(response_id, service.name, e)
                    continue
                response_aggregator.aggregate_response(response_id, service.name, service_response)
            else:
                # TODO: perform requests asynchronously and aggregate responses on returns
                raise NotImplementedError
        return response_id


request_distributor = RequestDistributor()


def get_request_distributor():
    return request_distributor
