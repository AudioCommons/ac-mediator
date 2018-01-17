import uuid
import redis
import json
import datetime
from ac_mediator.exceptions import *
from django.conf import settings
from django.urls import reverse


RESPONSE_STATUS_FINISHED = 'FI'
RESPONSE_STATUS_PROCESSING = 'PR'
RESPONSE_STATUS_NEW = 'NEW'


class RedisStoreBackend(object):
    """
    Redis-bases backend for storing current (ongoing) responses. See ResponseAggregator for more info.
    """

    r = None

    def __init__(self):
        self.r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

    def new_response(self, init_response_contents):
        response_id = uuid.uuid4()
        self.r.set(response_id, json.dumps(init_response_contents), ex=settings.RESPONSE_EXPIRY_TIME)
        return response_id

    def get_response(self, response_id):
        try:
            response = self.r.get(response_id)
        except redis.exceptions.ResponseError:
            # Can happen if we're trying to get a response from a key whose contents are not from an API response
            return None
        if response is None:
            return None
        try:
            return json.loads(response.decode("utf-8"))
        except json.decoder.JSONDecodeError:
            # Can happen if we're trying to get a response from a key whose contents are not from an API response
            return None

    def set_response(self, response_id, response_contents):
        self.r.set(response_id, json.dumps(response_contents), ex=settings.RESPONSE_EXPIRY_TIME)

    def delete_response(self, response_id):
        self.r.delete(response_id)

    def get_all_response_keys(self):
        return self.r.keys('*')


class ResponseAggregator(object):
    """
    The response aggregator is in charge of maintaining a pool of request responses and keep on aggregating
    responses from different services at the moment these are received. It uses a redis-based store
    (RedisStoreBackend) to share response data within all ac_mediator processes and celery workers.
    The ReponseAggregator implement a ResponseAggregator.collect_response method which is given
    a 'response_id' object and will return the current responses that have been aggregated for the
    given response_id at the time of calling the method. This is used for the /api/collect endpoint
    and this is how API clients can iterativelly pull results as soon as these are received (NOTE: this
    only makes sense when wait_until_complete=False in the RequestDistributor)
    """

    def __init__(self, store_backend=RedisStoreBackend):
        self.store = store_backend()

    def create_response(self, n_expected_responses):
        response_id = self.store.new_response({
            'meta': {
                'response_id': None,  # Will be filled in self.collect_response
                'status': RESPONSE_STATUS_NEW,
                'n_expected_responses': n_expected_responses,
                'n_received_responses': 0,
                'sent_timestamp': str(datetime.datetime.now())
            },
            'contents': dict(),
            'warnings': dict(),
            'errors': dict(),
        })
        return response_id

    def set_response_to_processing(self, response_id):
        response = self.store.get_response(response_id)
        response['meta']['status'] = RESPONSE_STATUS_PROCESSING
        self.store.set_response(response_id, response)

    def set_response_to_finished(self, response_id):
        response = self.store.get_response(response_id)
        response['meta']['status'] = RESPONSE_STATUS_FINISHED
        self.store.set_response(response_id, response)

    def aggregate_response(self, response_id, service_name, response_contents, warnings=None):
        response = self.store.get_response(response_id)
        response['meta']['n_received_responses'] += 1
        if isinstance(response_contents, ACException) or isinstance(response_contents, ACAPIException):
            # If response content is error, add to errors dict
            response['errors'][service_name] = {
                'status_code': response_contents.status,
                'type': response_contents.__class__.__name__,
                'detail': response_contents.msg,
            }
        else:
            # If response content is ok, add to contents dict
            response['contents'][service_name] = response_contents
            # If response content has warnings, add them to the warnings dict
            if warnings:
                response['warnings'][service_name] = warnings
        if response['meta']['n_received_responses'] == response['meta']['n_expected_responses']:
            response['meta']['status'] = RESPONSE_STATUS_FINISHED
        self.store.set_response(response_id, response)

    def collect_response(self, response_id, format='json'):
        response = self.store.get_response(response_id)
        to_return = None
        if response is None:
            return to_return
        if format == 'json':
            to_return = response.copy()
            to_return['meta']['response_id'] = response_id  # Add response_id to returned dictionary
            to_return['meta']['collect_url'] = settings.BASE_URL + '{0}?rid={1}'.format(reverse('api-collect'), response_id)  # Add collect url for convinience
            to_return['meta']['current_timestamp'] = str(datetime.datetime.now())
            if response['meta']['status'] == RESPONSE_STATUS_FINISHED and settings.DELETE_RESPONSES_AFTER_CONSUMED:
                self.store.delete_response(response_id)  # If response has been all loaded, delete it from pool
        elif format == 'jsonld':
            from rdflib import Graph, plugin, URIRef, Literal, Namespace, BNode
            from rdflib.namespace import RDF
            from rdflib.serializer import Serializer
            g = Graph()
            n_ac = Namespace('https://m.audiocommons.org/ontology/response/')
            n_mo = Namespace('http://mo/')

            object1 = URIRef('https://m.audiocommons.org/api/v1/acid/Freesound:1234/')
            g.add((object1, RDF.type, n_mo.AudioFile))
            g.add((object1, n_ac.creator, Literal('Name Surename')))
            g.add((object1, n_ac.friend_of_creator, Literal('Name Surename')))

            object2 = URIRef('https://m.audiocommons.org/api/v1/acid/Freesound:1235/')
            g.add((object2, RDF.type, n_mo.AudioFile))
            g.add((object2, n_ac.creator, Literal('Name2 Surename2')))

            r_ref = BNode()
            g.add((r_ref, RDF.type, n_ac.response))
            g.add((r_ref, n_ac.response_contents, object1))
            g.add((r_ref, n_ac.response_contents, object2))





            to_return = g.serialize(format='json-ld', context={
                '@ac': 'https://m.audiocommons.org/ontology/response/',
                '@mo': 'http://mo/'
            })
            to_return = json.loads(to_return.decode("utf-8"))
        return to_return


response_aggregator = ResponseAggregator()


def get_response_aggregator():
    return response_aggregator
