from services.classes import *


class FakeService(BaseACService, ACServiceAuthMixin):
    NAME = 'Fake service'
