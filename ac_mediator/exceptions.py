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


class ACLicesningException(ACException):
    pass


class ACDownloadException(ACException):
    pass


class ACPageNotFound(ACException):

    msg = 'Page not found.'
    status = status.HTTP_404_NOT_FOUND


# AC API Exceptions
# We generally use exceptions provided by rest_framework, we only add here new exceptions that are not included
# in the rest_framework package.

class ACAPIInvalidUrl(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid URL.'
    default_code = 'invalid_url'


class ACAPIServiceDoesNotExist(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Requested service does not exist.'
    default_code = 'service_does_not_exist'
