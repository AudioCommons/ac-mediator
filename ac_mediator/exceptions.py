class ACException(Exception):
    pass


class ImproperlyConfiguredACService(ACException):
    pass


class ACServiceDoesNotExist(ACException):
    pass


class UnexpectedServiceResourceField(ACException):
    pass
