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
