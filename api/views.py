from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from api.request_distributor import get_request_distributor
from api.response_aggregator import get_response_aggregator
from services.management import get_available_services
from services.mixins.constants import SEARCH_TEXT_COMPONENT, LICENSING_COMPONENT

request_distributor = get_request_distributor()
response_aggregator = get_response_aggregator()


class Services(GenericAPIView):

    def get(self, request,  *args, **kwargs):
        services = get_available_services()
        return Response({
            'count': len(services),
            'services': {service.name: {
                'id': service.id,
                'url': service.url,
                'components': service.implemented_components
            } for service in services}
        })


class TextSearch(GenericAPIView):

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
        response = response_aggregator.collect_response(response_id)
        return Response(response)


class Licensing(GenericAPIView):

    def get(self, request,  *args, **kwargs):
        response_id = request_distributor.process_request({
            'component': LICENSING_COMPONENT,
            'method': 'get_licensing_url',
            'kwargs': {'acid': request.GET.get('acid')}
        })

        # Because current implementation of request_distributor is synchronous, we can simply
        # collect response here and return it. Otherwise we should probably simply return the
        # response_id and the client should be in charge of iteratively checking if the response
        # is ready to be returned
        response = response_aggregator.collect_response(response_id)
        return Response(response)
