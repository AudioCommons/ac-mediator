from rest_framework.exceptions import APIException
from rest_framework import status


# AC Service exceptions

class ACException(Exception):
    msg = None
    status = None

    def __init__(self, msg=None, status=None):

        # Set defaults (if not set in subclass)
        if self.msg is None:
            self.msg = ""
        if self.status is None:
            self.msg = -1

        # Override with arguments (if any)
        if msg is not None:
            self.msg = msg
        if status is not None:
            self.status = status

    def __repr__(self):
        return self.msg


class ImproperlyConfiguredACService(ACException):
    pass


class ACServiceDoesNotExist(ACException):
    pass


class ACFieldTranslateException(ACException):
    pass


# AC API Exceptions

class ACAPIException(APIException):

    @property
    def msg(self):
        return self.detail or self.default_detail

    @property
    def status(self):
        return self.status_code


class ACAPIInvalidUrl(ACAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid URL.'
    default_code = 'invalid_url'


class ACAPIServiceDoesNotExist(ACAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Requested service does not exist.'
    default_code = 'service_does_not_exist'


class ACAPIPageNotFound(ACAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Page not found.'
    default_code = 'page_not_found'


class ACAPIResourceDoesNotExist(ACAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Requested resource does not exist.'
    default_code = 'resource_not_found'


class ACAPIResponseDoesNotExist(ACAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Requested response does not exist.'
    default_code = 'response_not_found'


class ACAPIInvalidACID(ACAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid Audio Commons Unique Identifier.'
    default_code = 'invalid_acid'


class ACAPIInvalidCredentialsForService(ACAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Credentials to access third party service are invalid or have expired.'
    default_code = 'invalid_credentials_for_service'


class ACAPIBadRequest(ACAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Bad request.'
    default_code = 'bad_request'
