class ACException(Exception):
    pass


class ImproperlyConfiguredACService(ACException):
    pass


class ACServiceDoesNotExist(ACException):
    pass


class ACFieldTranslateException(ACException):
    pass


class ACLicesningException(ACException):
    pass
