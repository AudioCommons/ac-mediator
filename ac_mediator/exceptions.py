from rest_framework.exceptions import APIException
from rest_framework import status


# AC Service exceptions

class ACException(Exception):

    def __init__(self, msg="", status=-1):
        self.msg = msg
        self.status = status

    def __repr__(self):
        return self.msg


class ImproperlyConfiguredACService(ACException):
    pass


class ACServiceDoesNotExist(ACException):
    pass


class ACFieldTranslateException(ACException):
    pass


class ACLicesningException(ACException):
    pass


# AC API Exceptions
# We generally use exceptions provided by rest_framework, we only add here new exceptions that are not included
# in the rest_framework package.

class ACAPIInvalidUrl(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid URL.'
    default_code = 'invalid_url'
