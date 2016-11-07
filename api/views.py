from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from api.request_distributor import get_request_distributor
from api.results_aggregator import get_results_aggregator
from services.mixins.constants import SEARCH_TEXT_COMPONENT

request_distributor = get_request_distributor()
results_aggregator = get_results_aggregator()


class Services(GenericAPIView):

    def get(self, request,  *args, **kwargs):
        return Response({'message': 'this is the description of services'})


class Search(GenericAPIView):

    def get(self, request,  *args, **kwargs):
        response_id = request_distributor.process_request({
            'component': SEARCH_TEXT_COMPONENT,
            'method': 'text_search',
            'kwargs': {'query': request.GET.get('q')}
        })

        # Because current implementation of request_distributor is synchronous, we can simply
        # collect response here and return it. Otherwise we should probably simply return the
        # response_id and the client should be in charge of iteratively checking if the response
        # is ready to be returned
        response = results_aggregator.collect_response(response_id)
        return Response(response)
