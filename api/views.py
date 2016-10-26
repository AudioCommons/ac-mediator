from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


class Services(GenericAPIView):

    def get(self, request,  *args, **kwargs):
        return Response({'message': 'this is the description of services'})


class Search(GenericAPIView):

    def get(self, request,  *args, **kwargs):
        return Response({'message': 'this is the search endpoint'})

