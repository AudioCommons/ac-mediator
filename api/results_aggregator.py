import uuid


RESPONSE_STATUS_FINISHED = 'FI'
RESPONSE_STATUS_PROCESSING = 'PR'
RESPONSE_STATUS_NEW = 'NEW'


class ResultsAggregator(object):
    """
    The results aggregator is in charge ok maintaining a pool of request responses
    and keep on aggregating responses from different services at the moment these are received.
    NOTE: Currently we just have a very simple implementation where responses are stored in a dictionary
    in memory (self.current_responses). This works because there is a single instance of ResultsAggregator.
    In production we'll need some system that shares these responses across instances of the Audio Commons
    mediator. Maybe we could use some database-like backed or in-memory caching backend like memcached.
    To use a different backend we should basically override 'create_response', 'get_response' and
    'delete_response' methods.
    """
    current_responses = None

    def __init__(self):
        self.current_responses = dict()

    def create_response(self, n_expected_responses):
        response_id = uuid.uuid4()
        self.current_responses[response_id] = {
            'status': RESPONSE_STATUS_NEW,
            'contents': dict(),
            'n_expected_responses': n_expected_responses,
            'n_received_responses': 0,
        }
        return response_id

    def get_response(self, response_id):
        return self.current_responses[response_id]

    def delete_response(self, response_id):
        del self.current_responses[response_id]

    def set_response_to_processing(self, response_id):
        self.get_response(response_id)['status'] = RESPONSE_STATUS_PROCESSING

    def set_response_to_finished(self, response_id):
        self.get_response(response_id)['status'] = RESPONSE_STATUS_FINISHED

    def aggregate_results(self, response_id, service_name, results):
        response = self.get_response(response_id)
        response['contents'][service_name] = results
        response['n_received_responses'] += 1
        if response['n_received_responses'] == response['n_expected_responses']:
            self.set_response_to_finished(response_id)

    def collect_response(self, response_id):
        response = self.get_response(response_id)
        to_return = response.copy()
        if response['status'] == RESPONSE_STATUS_FINISHED:
            self.delete_response(response_id)  # If response has been all loaded, delete it from pool
        return to_return


results_aggregator = ResultsAggregator()


def get_results_aggregator():
    return results_aggregator
