import uuid
import redis
import json
from ac_mediator.exceptions import ACException
from django.conf import settings


RESPONSE_STATUS_FINISHED = 'FI'
RESPONSE_STATUS_PROCESSING = 'PR'
RESPONSE_STATUS_NEW = 'NEW'


class DictStoreBackend(object):
    """
    Basic backend for storing current (ongoing) responses. See ResponseAggregator for more info.
    """

    current_responses = None

    def __init__(self):
        self.current_responses = dict()

    def new_response(self, init_response_contents):
        response_id = uuid.uuid4()
        self.current_responses[response_id] = init_response_contents
        return response_id

    def get_response(self, response_id):
        return self.current_responses[response_id]

    def set_response(self, response_id, response_contents):
        self.current_responses[response_id] = response_contents

    def delete_response(self, response_id):
        del self.current_responses[response_id]


class RedisStoreBackend(object):
    """
    Basic backend for storing current (ongoing) responses. See ResponseAggregator for more info.
    """

    r = None

    def __init__(self):
        self.r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

    def new_response(self, init_response_contents):
        response_id = uuid.uuid4()
        self.r.set(response_id, json.dumps(init_response_contents))
        return response_id

    def get_response(self, response_id):
        response = self.r.get(response_id)
        if response is None:
            return None
        return json.loads(response.decode("utf-8"))

    def set_response(self, response_id, response_contents):
        self.r.set(response_id, json.dumps(response_contents))

    def delete_response(self, response_id):
        self.r.delete(response_id)


class ResponseAggregator(object):
    """
    The response aggregator is in charge of maintaining a pool of request responses and keep on aggregating
    responses from different services at the moment these are received.
    NOTE: Currently we just have a very simple implementation where responses are stored in a dictionary
    in memory (see DictStoreBackend). This works because there is a single instance of ResponseAggregator.
    In production we'll need some system that shares these responses across instances of the Audio Commons
    mediator. Maybe we could use some database-like backend or in-memory caching backend like memcached.
    To use a different backend we should basically implement a new backend class with 'new_response',
    'get_response', 'set_response' and 'delete_response' methods and pass its definition to the ReponseAggregator
    constructor (instead of the default DictStoreBackend).
    """

    def __init__(self, store_backend=RedisStoreBackend):
        self.store = store_backend()

    def create_response(self, n_expected_responses):
        response_id = self.store.new_response({
            'status': RESPONSE_STATUS_NEW,
            'contents': dict(),
            'errors': dict(),
            'n_expected_responses': n_expected_responses,
            'n_received_responses': 0,
        })
        return response_id

    def set_response_to_processing(self, response_id):
        response = self.store.get_response(response_id)
        response['status'] = RESPONSE_STATUS_PROCESSING
        self.store.set_response(response_id, response)

    def set_response_to_finished(self, response_id):
        response = self.store.get_response(response_id)
        response['status'] = RESPONSE_STATUS_FINISHED
        self.store.set_response(response_id, response)

    def aggregate_response(self, response_id, service_name, response_contents):
        response = self.store.get_response(response_id)
        response['n_received_responses'] += 1
        if isinstance(response_contents, ACException):
            # If response content is error, add to errors dict
            response['errors'][service_name] = {
                'status': response_contents.status,
                'type': response_contents.__class__.__name__,
                'message': response_contents.msg,
            }
        else:
            # If response content is ok, add to contents dict
            response['contents'][service_name] = response_contents
        if response['n_received_responses'] == response['n_expected_responses']:
            response['status'] = RESPONSE_STATUS_FINISHED
        self.store.set_response(response_id, response)

    def collect_response(self, response_id):
        response = self.store.get_response(response_id)
        if response is None:
            return None
        to_return = response.copy()
        if response['status'] == RESPONSE_STATUS_FINISHED:
            self.store.delete_response(response_id)  # If response has been all loaded, delete it from pool
        return to_return


response_aggregator = ResponseAggregator()


def get_response_aggregator():
    return response_aggregator
